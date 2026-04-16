using FileTagExplorer.Exceptions;
using FileTagExplorer.Infrastructure;
using FileTagExplorer.Models;

namespace FileTagExplorer.Services;

public sealed class TagStoreService(ITagRepository repository) : ITagStoreService
{
    public TagStore Load(string folderPath) => repository.Read(folderPath);

    public void Save(string folderPath, TagStore store) => repository.Write(folderPath, store);

    public void AddTag(TagStore store, string relativePath, string tagId)
    {
        if (!store.Files.TryGetValue(relativePath, out var list))
        {
            list = [];
            store.Files[relativePath] = list;
        }
        if (!list.Contains(tagId))
            list.Add(tagId);
    }

    public void RemoveTag(TagStore store, string relativePath, string tagId)
    {
        if (store.Files.TryGetValue(relativePath, out var list))
        {
            list.Remove(tagId);
            if (list.Count == 0)
                store.Files.Remove(relativePath);
        }
    }

    public Tag CreateTag(TagStore store, string name, string color)
    {
        // タグ名の一意性チェック（大文字小文字区別なし）(INV-002)
        if (store.Tags.Any(t => t.Name.Equals(name, StringComparison.OrdinalIgnoreCase)))
            throw new DuplicateTagNameException(name);

        var tag = new Tag(Guid.NewGuid().ToString(), name, color);
        store.Tags.Add(tag);
        return tag;
    }

    public void DeleteTag(TagStore store, string tagId)
    {
        store.Tags.RemoveAll(t => t.Id == tagId);

        // 全ファイルエントリから参照を除去 (INV-001)
        foreach (var key in store.Files.Keys.ToList())
        {
            store.Files[key].Remove(tagId);
            if (store.Files[key].Count == 0)
                store.Files.Remove(key);
        }
    }

    public void UpdateFileKey(TagStore store, string oldKey, string newKey)
    {
        // 移動後のタグ引き継ぎ (INV-007)
        if (!store.Files.TryGetValue(oldKey, out var tagIds)) return;
        store.Files.Remove(oldKey);
        store.Files[newKey] = tagIds;
    }

    public void CleanupOrphanedEntries(TagStore store, IEnumerable<string> existingRelativePaths)
    {
        var existing = existingRelativePaths.ToHashSet(StringComparer.OrdinalIgnoreCase);
        foreach (var key in store.Files.Keys.ToList())
        {
            if (!existing.Contains(key))
                store.Files.Remove(key);
        }
    }
}
