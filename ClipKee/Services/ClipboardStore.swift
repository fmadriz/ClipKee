import AppKit
import CryptoKit
import Observation

@MainActor
@Observable
final class ClipboardStore {
    private(set) var items: [ClipboardItem] = []

    private let pasteboard = NSPasteboard.general
    nonisolated(unsafe) private var monitoringTask: Task<Void, Never>?
    private var lastChangeCount: Int = NSPasteboard.general.changeCount
    private let maxItems = 1000
    private var suppressNextCapture = false

    init() {
        load()
        startMonitoring()
    }

    deinit {
        monitoringTask?.cancel()
    }

    func startMonitoring() {
        monitoringTask?.cancel()
        monitoringTask = Task { @MainActor [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .milliseconds(700))
                self?.pollPasteboardIfNeeded()
            }
        }
    }

    func pollPasteboardIfNeeded() {
        guard pasteboard.changeCount != lastChangeCount else { return }
        lastChangeCount = pasteboard.changeCount

        if suppressNextCapture {
            suppressNextCapture = false
            return
        }

        if let item = makeCurrentClipboardItem() {
            insertIfNeeded(item)
        }
    }

    func recopy(_ item: ClipboardItem) {
        suppressNextCapture = true
        pasteboard.clearContents()

        switch item.kind {
        case .text:
            if let text = item.text {
                pasteboard.setString(text, forType: .string)
            }
        case .image:
            if let data = item.imageData, let image = NSImage(data: data) {
                pasteboard.writeObjects([image])
            }
        case .file:
            if let paths = item.filePaths {
                let urls = paths.map { URL(fileURLWithPath: $0) as NSURL }
                pasteboard.writeObjects(urls)
            }
        }

        lastChangeCount = pasteboard.changeCount
    }

    func delete(_ item: ClipboardItem) {
        items.removeAll { $0.id == item.id }
        save()
    }

    func clearAll() {
        items.removeAll()
        save()
    }

    private func makeCurrentClipboardItem() -> ClipboardItem? {
        if let filePaths = extractFilePaths() {
            let fingerprint = sha256("file::\(filePaths.joined(separator: "\n"))")
            return ClipboardItem(kind: .file, filePaths: filePaths, fingerprint: fingerprint)
        }

        if let text = pasteboard.string(forType: .string)?
            .trimmingCharacters(in: .whitespacesAndNewlines),
           !text.isEmpty {
            let fingerprint = sha256("text::\(text)")
            return ClipboardItem(kind: .text, text: text, fingerprint: fingerprint)
        }

        if let data = extractImageData() {
            let fingerprint = sha256(data)
            return ClipboardItem(kind: .image, imageData: data, fingerprint: fingerprint)
        }

        return nil
    }

    private func extractFilePaths() -> [String]? {
        guard let urls = pasteboard.readObjects(
            forClasses: [NSURL.self],
            options: [.urlReadingFileURLsOnly: true]
        ) as? [URL], !urls.isEmpty else {
            return nil
        }

        let paths = urls.map(\.standardizedFileURL.path)
        return paths.isEmpty ? nil : paths
    }

    private func extractImageData() -> Data? {
        guard let image = NSImage(pasteboard: pasteboard) else { return nil }
        guard let tiff = image.tiffRepresentation else { return nil }
        guard let rep = NSBitmapImageRep(data: tiff) else { return tiff }
        return rep.representation(using: .png, properties: [:]) ?? tiff
    }

    private func insertIfNeeded(_ item: ClipboardItem) {
        if let existingIndex = items.firstIndex(where: { $0.fingerprint == item.fingerprint }) {
            let existing = items.remove(at: existingIndex)
            let refreshed = ClipboardItem(
                id: existing.id,
                kind: item.kind,
                text: item.text,
                imageData: item.imageData,
                filePaths: item.filePaths,
                createdAt: Date(),
                fingerprint: item.fingerprint
            )
            items.insert(refreshed, at: 0)
        } else {
            items.insert(item, at: 0)
        }

        if items.count > maxItems {
            items = Array(items.prefix(maxItems))
        }

        save()
    }

    private func sha256(_ string: String) -> String {
        let digest = SHA256.hash(data: Data(string.utf8))
        return digest.map { String(format: "%02x", $0) }.joined()
    }

    private func sha256(_ data: Data) -> String {
        let digest = SHA256.hash(data: data)
        return digest.map { String(format: "%02x", $0) }.joined()
    }

    private var storageURL: URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        let folder = base.appendingPathComponent("ClipKee", isDirectory: true)

        if !FileManager.default.fileExists(atPath: folder.path) {
            try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        }

        return folder.appendingPathComponent("history.json")
    }

    private func save() {
        do {
            let data = try JSONEncoder().encode(items)
            try data.write(to: storageURL, options: .atomic)
        } catch {
            print("Save error: \(error)")
        }
    }

    private func load() {
        guard FileManager.default.fileExists(atPath: storageURL.path) else { return }

        do {
            let data = try Data(contentsOf: storageURL)
            items = try JSONDecoder().decode([ClipboardItem].self, from: data)
        } catch {
            print("Load error: \(error)")
            items = []
        }
    }
}
