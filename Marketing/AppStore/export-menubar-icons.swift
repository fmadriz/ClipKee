#!/usr/bin/env swift
import AppKit

let outDir = CommandLine.arguments.count > 1
    ? URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
    : URL(fileURLWithPath: FileManager.default.currentDirectoryPath, isDirectory: true)
    .appendingPathComponent("menubar-icons", isDirectory: true)

try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

struct IconSpec {
    let fileName: String
    let symbol: String
    let pointSize: CGFloat
    let weight: NSFont.Weight
}

let icons: [IconSpec] = [
    IconSpec(fileName: "apple", symbol: "apple.logo", pointSize: 13, weight: .medium),
    IconSpec(fileName: "control-center", symbol: "switch.2", pointSize: 14, weight: .medium),
    IconSpec(fileName: "wifi", symbol: "wifi", pointSize: 13.5, weight: .medium),
    IconSpec(fileName: "battery", symbol: "battery.100", pointSize: 13.5, weight: .medium),
    IconSpec(fileName: "spotlight", symbol: "magnifyingglass", pointSize: 13, weight: .medium),
    IconSpec(fileName: "clipkee", symbol: "list.clipboard.fill", pointSize: 14, weight: .bold),
]

func export(_ spec: IconSpec) throws {
    let config = NSImage.SymbolConfiguration(pointSize: spec.pointSize, weight: spec.weight)
    guard let image = NSImage(systemSymbolName: spec.symbol, accessibilityDescription: nil)?
        .withSymbolConfiguration(config)
    else {
        throw NSError(domain: "export-menubar-icons", code: 1, userInfo: [
            NSLocalizedDescriptionKey: "Missing symbol: \(spec.symbol)",
        ])
    }

    let scale: CGFloat = 2
    let dim = max(image.size.width, image.size.height) * scale
    let pixels = Int(ceil(dim))

    guard let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: pixels,
        pixelsHigh: pixels,
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    ) else {
        throw NSError(domain: "export-menubar-icons", code: 2, userInfo: [
            NSLocalizedDescriptionKey: "Failed to create bitmap for \(spec.symbol)",
        ])
    }

    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
    rep.size = NSSize(width: dim, height: dim)

    NSColor.clear.set()
    NSRect(x: 0, y: 0, width: dim, height: dim).fill()

    NSColor.black.set()
    let iconSize = NSSize(width: dim * 0.88, height: dim * 0.88)
    let origin = NSPoint(x: (dim - iconSize.width) / 2, y: (dim - iconSize.height) / 2)
    image.draw(in: NSRect(origin: origin, size: iconSize))

    NSGraphicsContext.restoreGraphicsState()

    let out = outDir.appendingPathComponent("\(spec.fileName).png")
    guard let data = rep.representation(using: .png, properties: [:]) else {
        throw NSError(domain: "export-menubar-icons", code: 3, userInfo: [
            NSLocalizedDescriptionKey: "Failed to encode PNG for \(spec.symbol)",
        ])
    }
    try data.write(to: out)
    print(out.path)
}

for spec in icons {
    try export(spec)
}
