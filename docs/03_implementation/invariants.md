---
status: active
tracks:
  - src/FileTagExplorer/Models/**
  - src/FileTagExplorer/Services/**
  - src/FileTagExplorer/Infrastructure/**
---

# invariants.md — 不変条件

## 定義

不変条件（Invariant）は、システムの状態が常に満たさなければならない条件です。
実装・テスト・コードレビューの際に必ずこれらを確認してください。

---

## INV-001: TagStore の整合性

**タグIDの参照整合性**

> `TagStore.Files` の値リストに含まれるタグIDは、  
> 必ず `TagStore.Tags` に存在するエントリのIDでなければならない。  
> ただし、ロード時に孤立IDが存在する場合は無視する（削除はしない）。  
> タグを削除する際は、`Files` 内の全参照を同時に削除しなければならない。

検証方法:
```csharp
// TagStoreService.RemoveTag() 後に確認
var removedId = tag.Id;
Assert.DoesNotContain(removedId, store.Files.SelectMany(f => f.Value));
```

---

## INV-002: タグ名の一意性

**タグ名の重複禁止**

> `TagStore.Tags` 内のタグ名（`Tag.Name`）は大文字小文字を区別せず一意でなければならない。  
> 同名のタグ作成は禁止。

検証方法:
```csharp
var names = store.Tags.Select(t => t.Name.ToLowerInvariant());
Assert.Equal(names.Distinct().Count(), store.Tags.Count);
```

---

## INV-003: ファイル一覧のスコープ

**ファイルは開いたフォルダの配下のみ、.filetags は除外**

> `MainViewModel.Files` が保持するファイルエントリは、  
> 現在開いているフォルダとその下位階層のファイルのみでなければならない。  
> `.filetags` ファイル自身は含まない。

検証方法:
```csharp
foreach (var entry in mainVm.Files)
{
    // 開いたフォルダの配下であること
    Assert.True(entry.FullPath.StartsWith(currentFolderPath,
        StringComparison.OrdinalIgnoreCase));
    // .filetags は含まない
    Assert.NotEqual(".filetags", entry.Name,
        StringComparer.OrdinalIgnoreCase);
}
```

---

## INV-004: .filetags の原子的書き込み

**書き込みは中断に対してアトミックでなければならない**

> `.filetags` の保存は必ず一時ファイル経由のアトミック置換で行う。  
> 直接上書き保存（`File.WriteAllText` で直接書き込む）は禁止。

実装パターン:
```csharp
// 正しい実装
var tmpPath = Path.GetTempFileName();
await File.WriteAllTextAsync(tmpPath, json);
File.Move(tmpPath, targetPath, overwrite: true);

// 禁止
await File.WriteAllTextAsync(targetPath, json); // ← NG
```

---

## INV-005: 移動操作のスコープ制約

**移動先は開いたフォルダ配下のフォルダのみ（ルート自身を含む）**

> ファイル移動の移動先パスは、現在開いているフォルダまたはその下位フォルダでなければならない。  
> 開いたフォルダの外への移動は禁止。

検証方法:
```csharp
Assert.True(destinationPath.StartsWith(currentFolderPath,
    StringComparison.OrdinalIgnoreCase));
```

---

## INV-006: バージョン互換性

**未知のスキーマバージョンは拒否する**

> `.filetags` ファイルの `version` フィールドが現在サポートするバージョン（`1`）と  
> 一致しない場合、ファイルのロードを中断し例外をスローしなければならない。  
> 将来バージョンへの暗黙的なダウングレード変換は禁止。

検証方法:
```csharp
var json = """{"version": 99, "tags": [], "files": {}}""";
Assert.Throws<UnsupportedVersionException>(
    () => repository.Read(folderPath));
```

---

## INV-007: 移動後のタグデータ引き継ぎ

**ファイル移動時は .filetags のキーを更新してタグを引き継ぐ**

> ファイルを移動した場合、`.filetags` 内のキー（相対パス）を  
> 旧パスから新パスに更新し、タグ情報は失ってはならない。  
> 移動後に旧キーのエントリが残ってはならない。

検証方法:
```csharp
var oldKey = "drafts/report.pdf";
var newKey = "archived/report.pdf";
var originalTagIds = store.Files[oldKey].ToList();
// 移動後
store = service.UpdateFileKey(store, oldKey, newKey);
Assert.False(store.Files.ContainsKey(oldKey));
Assert.True(store.Files.ContainsKey(newKey));
Assert.Equal(originalTagIds, store.Files[newKey]);
```

---

## テスト対応表

| 不変条件 | テストクラス                                 | AC-ID  |
|---------|----------------------------------------------|--------|
| INV-001 | `TagStoreServiceTests.RemoveTag_*`           | AC-005 |
| INV-002 | `TagStoreServiceTests.CreateTag_*`           | AC-006 |
| INV-003 | `FileSystemServiceTests.GetFilesAsync_*`     | AC-002 |
| INV-004 | `JsonTagRepositoryTests.Write_*`             | AC-004 |
| INV-005 | `FileSystemServiceTests.MoveFiles_*`         | AC-010 |
| INV-006 | `JsonTagRepositoryTests.Read_*`              | —      |
| INV-007 | `TagStoreServiceTests.UpdateFileKey_*`       | AC-009 |
