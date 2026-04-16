using FileTagExplorer.Services;
using FluentAssertions;

namespace FileTagExplorer.Tests.Services;

public sealed class FileSystemServiceTests : IDisposable
{
    private readonly string _tempFolder;
    private readonly FileSystemService _sut = new();

    public FileSystemServiceTests()
    {
        _tempFolder = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        Directory.CreateDirectory(_tempFolder);
    }

    public void Dispose() => Directory.Delete(_tempFolder, recursive: true);

    // ─── GetFilesAsync ────────────────────────────────────────────
    [Fact]
    [Trait("AC", "AC-002")]
    public async Task GetFilesAsync_ReturnsFilesFromRootAndSubfolders()
    {
        File.WriteAllText(Path.Combine(_tempFolder, "root.txt"), "");
        var subDir = Directory.CreateDirectory(Path.Combine(_tempFolder, "sub"));
        File.WriteAllText(Path.Combine(subDir.FullName, "nested.txt"), "");

        var files = await _sut.GetFilesAsync(_tempFolder).ToListAsync();

        files.Should().HaveCount(2);
        files.Should().Contain(f => f.Name == "root.txt" && f.RelativePath == "root.txt");
        files.Should().Contain(f => f.Name == "nested.txt" && f.RelativePath == "sub/nested.txt");
    }

    [Fact]
    [Trait("AC", "AC-002")]
    public async Task GetFilesAsync_ExcludesFiletagsFile_INV003()
    {
        File.WriteAllText(Path.Combine(_tempFolder, "data.csv"), "");
        File.WriteAllText(Path.Combine(_tempFolder, ".filetags"), "{}");

        var files = await _sut.GetFilesAsync(_tempFolder).ToListAsync();

        files.Should().ContainSingle().Which.Name.Should().Be("data.csv");
        files.Should().NotContain(f => f.Name == ".filetags");
    }

    [Fact]
    [Trait("AC", "AC-002")]
    public async Task GetFilesAsync_ReturnsCorrectRelativePaths()
    {
        var sub = Directory.CreateDirectory(Path.Combine(_tempFolder, "a", "b"));
        File.WriteAllText(Path.Combine(sub.FullName, "deep.md"), "");

        var files = await _sut.GetFilesAsync(_tempFolder).ToListAsync();

        files.Single().RelativePath.Should().Be("a/b/deep.md");
    }

    [Fact]
    [Trait("AC", "AC-002")]
    public async Task GetFilesAsync_ReturnsEmpty_WhenFolderIsEmpty()
    {
        var files = await _sut.GetFilesAsync(_tempFolder).ToListAsync();

        files.Should().BeEmpty();
    }

    [Fact]
    public async Task GetFilesAsync_RespectsCancellation()
    {
        for (int i = 0; i < 10; i++)
            File.WriteAllText(Path.Combine(_tempFolder, $"file{i}.txt"), "");

        using var cts = new CancellationTokenSource();
        cts.Cancel();

        var act = async () => await _sut.GetFilesAsync(_tempFolder, cts.Token).ToListAsync();

        await act.Should().ThrowAsync<OperationCanceledException>();
    }

    // ─── GetFolderTree ────────────────────────────────────────────
    [Fact]
    public void GetFolderTree_ReturnsRootWithChildren()
    {
        Directory.CreateDirectory(Path.Combine(_tempFolder, "alpha"));
        Directory.CreateDirectory(Path.Combine(_tempFolder, "beta"));

        var tree = _sut.GetFolderTree(_tempFolder);

        tree.RelativePath.Should().BeEmpty(); // ルートは空文字
        tree.Children.Should().HaveCount(2);
        tree.Children.Should().Contain(n => n.RelativePath == "alpha");
        tree.Children.Should().Contain(n => n.RelativePath == "beta");
    }

    [Fact]
    public void GetFolderTree_BuildsNestedHierarchy()
    {
        Directory.CreateDirectory(Path.Combine(_tempFolder, "parent", "child"));

        var tree = _sut.GetFolderTree(_tempFolder);

        var parent = tree.Children.Should().ContainSingle().Subject;
        parent.RelativePath.Should().Be("parent");
        parent.Children.Should().ContainSingle()
            .Which.RelativePath.Should().Be("parent/child");
    }

    // ─── MoveFile ─────────────────────────────────────────────────
    [Fact]
    [Trait("AC", "AC-009")]
    public void MoveFile_MovesFileToDestination()
    {
        var src = Path.Combine(_tempFolder, "move_me.txt");
        File.WriteAllText(src, "content");
        var destDir = Directory.CreateDirectory(Path.Combine(_tempFolder, "dest")).FullName;

        _sut.MoveFile(src, destDir);

        File.Exists(src).Should().BeFalse();
        File.Exists(Path.Combine(destDir, "move_me.txt")).Should().BeTrue();
    }

    [Fact]
    [Trait("AC", "AC-010")]
    public void MoveFile_WithOverwrite_ReplacesExistingFile()
    {
        var src = Path.Combine(_tempFolder, "file.txt");
        File.WriteAllText(src, "new content");
        var destDir = Directory.CreateDirectory(Path.Combine(_tempFolder, "dest")).FullName;
        File.WriteAllText(Path.Combine(destDir, "file.txt"), "old content");

        _sut.MoveFile(src, destDir, overwrite: true);

        File.ReadAllText(Path.Combine(destDir, "file.txt")).Should().Be("new content");
    }
}

// IAsyncEnumerable の ToListAsync ヘルパー
file static class AsyncEnumerableExtensions
{
    public static async Task<List<T>> ToListAsync<T>(
        this IAsyncEnumerable<T> source, CancellationToken ct = default)
    {
        var list = new List<T>();
        await foreach (var item in source.WithCancellation(ct))
            list.Add(item);
        return list;
    }
}
