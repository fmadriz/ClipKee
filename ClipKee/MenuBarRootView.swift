import SwiftUI
import AppKit

struct MenuBarRootView: View {
    @Environment(ClipboardStore.self) private var store
    @Environment(\.controlActiveState) private var controlActiveState
    @State private var isSearchVisible = false
    @State private var searchText = ""
    @State private var scrollResetID = UUID()
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
        .frame(width: 360, height: 560)
        .background(.regularMaterial)
        .onChange(of: controlActiveState) { _, newValue in
            if newValue == .key {
                resetToInitialState()
            }
        }
    }

    private func resetToInitialState() {
        isSearchVisible = false
        searchText = ""
        isSearchFocused = false
        scrollResetID = UUID()
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
                let willShowSearch = !isSearchVisible
                withAnimation(.easeInOut(duration: 0.2)) {
                    isSearchVisible = willShowSearch
                    if !willShowSearch {
                        searchText = ""
                        isSearchFocused = false
                    }
                }
                if willShowSearch {
                    DispatchQueue.main.async {
                        isSearchFocused = true
                    }
                }
            } label: {
                Image(systemName: isSearchVisible ? "magnifyingglass.circle.fill" : "magnifyingglass")
                    .font(.title3)
                    .foregroundStyle(isSearchVisible ? .primary : .secondary)
            }
            .buttonStyle(.plain)
            .help(isSearchVisible ? String(localized: "Hide search") : String(localized: "Search text entries"))

            Button {
                NSApplication.shared.terminate(nil)
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
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
        .background(Color.primary.opacity(0.04))
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "doc.on.clipboard")
                .font(.system(size: 28))
                .foregroundStyle(.secondary)

            Text("Nothing saved yet")
                .font(.headline)

            Text("Copy text or images with Cmd+C or from the context menu, and they will appear here.")
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
                store.clearAll()
            }
            .buttonStyle(.plain)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 10)
    }
}
