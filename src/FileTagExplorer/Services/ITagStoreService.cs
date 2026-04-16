using FileTagExplorer.Models;

namespace FileTagExplorer.Services;

public interface ITagStoreService
{
    TagStore Load(string folderPath);
    void Save(string folderPath, TagStore store);

    /// <summary>ファイルにタグを付与する。</summary>
    void AddTag(TagStore store, string relativePath, string tagId);

    /// <summary>ファイルからタグを削除する。</summary>
    void RemoveTag(TagStore store, string relativePath, string tagId);

    /// <summary>新しいタグを定義に追加する。同名は例外。</summary>
    Tag CreateTag(TagStore store, string name, string color);

    /// <summary>タグを削除し、全ファイルエントリからも除去する（INV-001）。</summary>
    void DeleteTag(TagStore store, string tagId);

    /// <summary>移動後のファイルキーを更新してタグを引き継ぐ（INV-007）。</summary>
    void UpdateFileKey(TagStore store, string oldKey, string newKey);

    /// <summary>実際に存在しないファイルのエントリを削除する（ゴミ掃除）。</summary>
    void CleanupOrphanedEntries(TagStore store, IEnumerable<string> existingRelativePaths);
}
