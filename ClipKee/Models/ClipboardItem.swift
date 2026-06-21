import Foundation

struct ClipboardItem: Identifiable, Codable, Equatable {
    enum Kind: String, Codable {
        case text
        case image
        case file
    }

    let id: UUID
    let kind: Kind
    let text: String?
    let imageData: Data?
    let filePaths: [String]?
    let createdAt: Date
    let fingerprint: String

    init(
        id: UUID = UUID(),
        kind: Kind,
        text: String? = nil,
        imageData: Data? = nil,
        filePaths: [String]? = nil,
        createdAt: Date = Date(),
        fingerprint: String
    ) {
        self.id = id
        self.kind = kind
        self.text = text
        self.imageData = imageData
        self.filePaths = filePaths
        self.createdAt = createdAt
        self.fingerprint = fingerprint
    }
}
