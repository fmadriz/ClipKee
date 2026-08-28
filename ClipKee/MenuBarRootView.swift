import SwiftUI
import AppKit

struct MenuBarRootView: View {
    @Environment(ClipboardStore.self) private var store
    @Environment(\.controlActiveState) private var controlActiveState
    @State private var isSearchVisible = false
    @State private var searchText = ""
    @State private var scrollResetID = UUID()
    @State private var isSettingsPresented = false
    @State private var showClearConfirmation = false
    @State private var showQuitConfirmation = false
    @FocusState private var isSearchFocused: Bool

    private var filteredItems: [ClipboardItem] {
        let query = searchText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else { return store.items }

        return store.items.filter { item in
            guard item.kind == .text, let text = item.text else { return false }
            return text.localizedCaseInsensitiveContains(query)
        }
    }

    private var isFiltering: Bool {
        !searchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    var body: some View {
        ZStack {
            clipboardContent

            if isSettingsPresented {
                settingsOverlay
                    .transition(.opacity)
            }

            if showClearConfirmation {
                clearConfirmationOverlay
                    .transition(.opacity)
            }

            if showQuitConfirmation {
                quitConfirmationOverlay
                    .transition(.opacity)
            }
        }
        .frame(width: 360, height: 560)
        .background(.regularMaterial)
        .animation(.easeInOut(duration: 0.2), value: isSettingsPresented)
        .animation(.easeInOut(duration: 0.2), value: showClearConfirmation)
        .animation(.easeInOut(duration: 0.2), value: showQuitConfirmation)
        .onExitCommand {
            guard isSearchVisible,
                  !isSettingsPresented,
                  !showClearConfirmation,
                  !showQuitConfirmation else { return }
            closeSearch()
        }
        .onChange(of: controlActiveState) { _, newValue in
            if newValue == .key,
               !isSettingsPresented,
               !showClearConfirmation,
               !showQuitConfirmation {
                resetToInitialState()
            }
        }
    }

    private var quitConfirmationOverlay: some View {
        ZStack {
            Color.black.opacity(0.45)
                .contentShape(Rectangle())

            VStack(spacing: 16) {
                Text("Quit ClipKee?")
                    .font(.headline)
                    .multilineTextAlignment(.center)

                Text("ClipKee will stop running and won't capture new clipboard entries until you open it again.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 240)

                HStack(spacing: 12) {
                    Button(String(localized: "Cancel")) {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            showQuitConfirmation = false
                        }
                    }
                    .keyboardShortcut(.cancelAction)

                    Button(String(localized: "Quit"), role: .destructive) {
                        NSApplication.shared.terminate(nil)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.red)
                }
            }
            .padding(20)
            .frame(width: 280)
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(Color.primary.opacity(0.08), lineWidth: 1)
            }
            .shadow(color: .black.opacity(0.25), radius: 24, y: 10)
        }
    }

    private var clearConfirmationOverlay: some View {
        ZStack {
            Color.black.opacity(0.45)
                .contentShape(Rectangle())

            VStack(spacing: 16) {
                Text("Clear clipboard history?")
                    .font(.headline)
                    .multilineTextAlignment(.center)

                Text("This will permanently remove all saved clipboard entries.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 240)

                HStack(spacing: 12) {
                    Button(String(localized: "Cancel")) {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            showClearConfirmation = false
                        }
                    }
                    .keyboardShortcut(.cancelAction)

                    Button(String(localized: "Clear all"), role: .destructive) {
                        store.clearAll()
                        scrollResetID = UUID()
                        withAnimation(.easeInOut(duration: 0.2)) {
                            showClearConfirmation = false
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.red)
                    .keyboardShortcut(.defaultAction)
                }
            }
            .padding(20)
            .frame(width: 280)
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(Color.primary.opacity(0.08), lineWidth: 1)
            }
            .shadow(color: .black.opacity(0.25), radius: 24, y: 10)
        }
    }

    private var settingsOverlay: some View {
        ZStack {
            Color.black.opacity(0.45)
                .contentShape(Rectangle())

            SettingsView(style: .floating) {
                withAnimation(.easeInOut(duration: 0.2)) {
                    isSettingsPresented = false
                }
            }
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(Color.primary.opacity(0.08), lineWidth: 1)
            }
            .shadow(color: .black.opacity(0.25), radius: 24, y: 10)
        }
    }

    private var clipboardContent: some View {
        VStack(spacing: 0) {
            header

            if isSearchVisible {
                searchBar
            }

            Divider()

            if store.items.isEmpty {
                emptyState
            } else if filteredItems.isEmpty {
                noResultsState
            } else {
                ScrollView {
                    LazyVStack(spacing: 10) {
                        ForEach(filteredItems) { item in
                            ClipboardCardView(item: item) {
                                store.recopy(item)
                            } onDelete: {
                                store.delete(item)
                            }
                        }
                    }
                    .padding(12)
                }
                .id(scrollResetID)
                .frame(maxHeight: 460)
            }

            Divider()

            footer
        }
    }

    private func resetToInitialState() {
        isSearchVisible = false
        searchText = ""
        isSearchFocused = false
        scrollResetID = UUID()
    }

    private func openSearch() {
        withAnimation(.easeInOut(duration: 0.2)) {
            isSearchVisible = true
        }
        DispatchQueue.main.async {
            isSearchFocused = true
        }
    }

    private func closeSearch() {
        withAnimation(.easeInOut(duration: 0.2)) {
            isSearchVisible = false
            searchText = ""
            isSearchFocused = false
        }
    }

    private var header: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("ClipKee")
                    .font(.system(size: 15, weight: .semibold, design: .rounded))

                Text("Clipboard history")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Button {
                if isSearchVisible {
                    closeSearch()
                } else {
                    openSearch()
                }
            } label: {
                Image(systemName: isSearchVisible ? "magnifyingglass.circle.fill" : "magnifyingglass")
                    .font(.title3)
                    .foregroundStyle(isSearchVisible ? .primary : .secondary)
            }
            .buttonStyle(.plain)
            .help(isSearchVisible ? String(localized: "Hide search") : String(localized: "Search text entries"))

            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    isSettingsPresented = true
                }
            } label: {
                Image(systemName: "gearshape")
                    .font(.title3)
                    .foregroundStyle(.secondary)
            }
            .buttonStyle(.plain)
            .help(String(localized: "Settings"))

            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    showQuitConfirmation = true
                }
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .font(.title3)
                    .foregroundStyle(.secondary)
            }
            .buttonStyle(.plain)
            .help(String(localized: "Quit"))
        }
        .padding(14)
    }

    private var searchBar: some View {
        HStack(spacing: 8) {
            Image(systemName: "magnifyingglass")
                .foregroundStyle(.secondary)

            TextField(String(localized: "Search copied text..."), text: $searchText)
                .textFieldStyle(.plain)
                .focused($isSearchFocused)
                .onKeyPress(.escape) {
                    closeSearch()
                    return .handled
                }

            if !searchText.isEmpty {
                Button {
                    searchText = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundStyle(.secondary)
                }
                .buttonStyle(.plain)
                .help(String(localized: "Clear search"))
            }

            Button {
                closeSearch()
            } label: {
                Image(systemName: "xmark")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(.secondary)
            }
            .buttonStyle(.plain)
            .help(String(localized: "Hide search"))
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .background(Color.primary.opacity(0.04))
        .onExitCommand {
            closeSearch()
        }
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "doc.on.clipboard")
                .font(.system(size: 28))
                .foregroundStyle(.secondary)

            Text("Nothing saved yet")
                .font(.headline)

            Text("Copy text, images, or files with Cmd+C or from the context menu, and they will appear here.")
                .font(.caption)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .frame(maxWidth: 240)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
    }

    private var noResultsState: some View {
        VStack(spacing: 12) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 28))
                .foregroundStyle(.secondary)

            Text("No matches")
                .font(.headline)

            Text(
                String(
                    format: String(localized: "no_results_format"),
                    searchText.trimmingCharacters(in: .whitespacesAndNewlines)
                )
            )
                .font(.caption)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .frame(maxWidth: 240)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
    }

    private var footer: some View {
        HStack {
            if isFiltering {
                Text(
                    String(
                        format: String(localized: "items_filtered_count_format"),
                        filteredItems.count,
                        store.items.count
                    )
                )
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } else {
                Text(
                    String(
                        format: String(localized: "items_count_format"),
                        store.items.count
                    )
                )
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Button(String(localized: "Clear")) {
                withAnimation(.easeInOut(duration: 0.2)) {
                    showClearConfirmation = true
                }
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
    }
}
