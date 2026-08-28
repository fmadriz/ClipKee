import SwiftUI

struct SettingsView: View {
    enum PresentationStyle {
        case floating
        case window
    }

    var style: PresentationStyle = .floating
    var onClose: (() -> Void)?

    @Environment(LaunchAtLoginManager.self) private var launchAtLoginManager
    @State private var launchAtLoginEnabled = true

    private var cardHeight: CGFloat {
        launchAtLoginManager.requiresApproval ? 380 : 320
    }

    var body: some View {
        VStack(spacing: 0) {
            header

            Divider()

            VStack(alignment: .leading, spacing: 16) {
                Toggle(isOn: $launchAtLoginEnabled) {
                    Text("Open ClipKee when I log in to this Mac")
                        .font(.body)
                }
                .toggleStyle(.checkbox)
                .onChange(of: launchAtLoginEnabled) { _, newValue in
                    launchAtLoginManager.isEnabled = newValue
                }

                if launchAtLoginManager.requiresApproval {
                    approvalNotice
                }
            }
            .padding(.horizontal, 20)
            .padding(.top, 20)
            .frame(maxWidth: .infinity, alignment: .leading)

            Spacer()

            Button(String(localized: "Done")) {
                onClose?()
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            Spacer()

            Text(appVersionLabel)
                .font(.caption)
                .foregroundStyle(.tertiary)
                .frame(maxWidth: .infinity)
                .padding(.bottom, 16)
        }
        .frame(
            width: style == .floating ? 300 : 380,
            height: style == .floating ? cardHeight : 300
        )
        .background(.regularMaterial)
        .onAppear {
            launchAtLoginManager.refreshStatus()
            launchAtLoginEnabled = launchAtLoginManager.isEnabled
        }
    }

    private var header: some View {
        HStack {
            Text("Settings")
                .font(.system(size: 15, weight: .semibold, design: .rounded))

            Spacer()
        }
        .padding(14)
    }

    private var approvalNotice: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(.orange)
                .font(.caption)

            VStack(alignment: .leading, spacing: 6) {
                Text("One more step in System Settings")
                    .font(.caption.weight(.semibold))

                Text("Enable ClipKee under Login Items so it can start automatically.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)

                Button("Open System Settings") {
                    launchAtLoginManager.openLoginItemsSettings()
                }
                .font(.caption)
                .buttonStyle(.plain)
                .foregroundStyle(.blue)
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.orange.opacity(0.12))
        .clipShape(RoundedRectangle(cornerRadius: 10))
    }

    private var appVersionLabel: String {
        let version = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0"
        return "ClipKee \(version)"
    }
}
