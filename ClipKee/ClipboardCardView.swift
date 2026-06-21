import SwiftUI
import AppKit

struct ClipboardCardView: View {
    let item: ClipboardItem
    let onCopy: () -> Void
    let onDelete: () -> Void

    @State private var showCopiedFeedback = false
    @State private var feedbackTask: Task<Void, Never>?

    var body: some View {
        Button(action: handleCopy) {
            cardContent
                .overlay {
                    if showCopiedFeedback {
                        copiedOverlay
                            .transition(.opacity)
                    }
                }
                .clipShape(RoundedRectangle(cornerRadius: 16))
        }
        .buttonStyle(.plain)
        .onDisappear {
            clearCopiedFeedback()
        }
        .onChange(of: item.id) { _, _ in
            clearCopiedFeedback()
        }
    }

    private var cardContent: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Label(kindLabel, systemImage: kindIcon)
                    .font(.caption)
                    .foregroundStyle(.secondary)

                Spacer()

                Text(item.createdAt, style: .time)
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }

            switch item.kind {
            case .text:
                Text(textPreview)
                    .font(.system(size: 13, weight: .regular, design: .rounded))
                    .foregroundStyle(.primary)
                    .lineLimit(4)
                    .multilineTextAlignment(.leading)
                    .frame(maxWidth: .infinity, alignment: .leading)
            case .image:
                if let image = nsImage {
                    ZStack {
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.secondary.opacity(0.08))

                        Image(nsImage: image)
                            .resizable()
                            .scaledToFit()
                            .frame(maxWidth: .infinity, maxHeight: 132)
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                            .padding(8)
                    }
                    .frame(height: 148)
                }
            case .file:
                VStack(alignment: .leading, spacing: 6) {
                    ForEach(fileNames, id: \.self) { name in
                        HStack(spacing: 8) {
                            Image(systemName: "doc.fill")
                                .foregroundStyle(.secondary)

                            Text(name)
                                .font(.system(size: 13, weight: .regular, design: .rounded))
                                .foregroundStyle(.primary)
                                .lineLimit(2)
                                .multilineTextAlignment(.leading)
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }

            HStack {
                Text(copyHint)
                    .font(.caption2)
                    .foregroundStyle(.secondary)

                Spacer()

                Button(role: .destructive, action: onDelete) {
                    Image(systemName: "trash")
                }
                .buttonStyle(.plain)
                .help(String(localized: "Delete"))
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(NSColor.windowBackgroundColor).opacity(0.95))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.primary.opacity(0.08), lineWidth: 1)
        )
    }

    private var copiedOverlay: some View {
        RoundedRectangle(cornerRadius: 16)
            .fill(Color.black.opacity(0.45))
            .overlay {
                VStack(spacing: 8) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title2)

                    Text(copiedMessage)
                        .font(.caption.weight(.semibold))
                }
                .foregroundStyle(.white)
            }
    }

    private func handleCopy() {
        onCopy()

        clearCopiedFeedback()
        withAnimation(.easeInOut(duration: 0.2)) {
            showCopiedFeedback = true
        }

        feedbackTask = Task { @MainActor in
            try? await Task.sleep(for: .seconds(1.2))
            guard !Task.isCancelled else { return }

            withAnimation(.easeInOut(duration: 0.25)) {
                showCopiedFeedback = false
            }
            feedbackTask = nil
        }
    }

    private func clearCopiedFeedback() {
        feedbackTask?.cancel()
        feedbackTask = nil
        showCopiedFeedback = false
    }

    private var kindLabel: String {
        switch item.kind {
        case .text:
            String(localized: "Text")
        case .image:
            String(localized: "Image")
        case .file:
            String(localized: "File")
        }
    }

    private var kindIcon: String {
        switch item.kind {
        case .text:
            "text.alignleft"
        case .image:
            "photo"
        case .file:
            "doc"
        }
    }

    private var copyHint: String {
        switch item.kind {
        case .text:
            String(localized: "Click to copy")
        case .image:
            String(localized: "Click to copy image")
        case .file:
            String(localized: "Click to copy file")
        }
    }

    private var copiedMessage: String {
        switch item.kind {
        case .text:
            String(localized: "Text copied")
        case .image:
            String(localized: "Image copied")
        case .file:
            String(localized: "File copied")
        }
    }

    private var fileNames: [String] {
        (item.filePaths ?? []).map { URL(fileURLWithPath: $0).lastPathComponent }
    }

    private var textPreview: String {
        (item.text ?? "")
            .replacingOccurrences(of: "\n", with: " ")
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private var nsImage: NSImage? {
        guard let data = item.imageData else { return nil }
        return NSImage(data: data)
    }
}
