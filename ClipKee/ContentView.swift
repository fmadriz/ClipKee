import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "paperclip.circle")
                .font(.system(size: 28))
                .foregroundStyle(.secondary)

            Text("ClipKee")
                .font(.title3.weight(.semibold))

            Text("This view is not used as the main screen. The app lives in the menu bar.")
                .font(.caption)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .frame(maxWidth: 240)
        }
        .padding(24)
        .frame(width: 320, height: 180)
    }
}

#Preview {
    ContentView()
}
