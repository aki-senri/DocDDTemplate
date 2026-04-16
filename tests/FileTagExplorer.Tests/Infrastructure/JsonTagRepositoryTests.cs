using FileTagExplorer.Exceptions;
using FileTagExplorer.Infrastructure;
using FileTagExplorer.Models;
using FluentAssertions;

namespace FileTagExplorer.Tests.Infrastructure;

public sealed class JsonTagRepositoryTests : IDisposable
{
    private readonly string _tempFolder;
    private readonly JsonTagRepository _sut = new();

    public JsonTagRepositoryTests()
    {
        _tempFolder = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        Directory.CreateDirectory(_tempFolder);
    }

    public void Dispose() => Directory.Delete(_tempFolder, recursive: true);

    [Fact]
    public void Read_ReturnsEmptyStore_WhenFileNotExists()
    {
        var store = _sut.Read(_tempFolder);

        store.Version.Should().Be(1);
        store.Tags.Should().BeEmpty();
        store.Files.Should().BeEmpty();
    }

    [Fact]
    public void Write_And_Read_RoundTrips_TagStore()
    {
        var original = new TagStore
        {
            Tags = [new Tag("id1", "重要", "#FF5722")],
            Files = { ["subdir/file.txt"] = ["id1"] },
        };

        _sut.Write(_tempFolder, original);
        var loaded = _sut.Read(_tempFolder);

        loaded.Tags.Should().HaveCount(1);
        loaded.Tags[0].Id.Should().Be("id1");
        loaded.Tags[0].Name.Should().Be("重要");
        loaded.Tags[0].Color.Should().Be("#FF5722");
        loaded.Files["subdir/file.txt"].Should().Contain("id1");
    }

    [Fact]
    public void Write_CreatesFileAtomically_ViaTemp()
    {
        // 内容を書いて読み直せる（アトミック書き込みの結果確認）
        var store = new TagStore { Tags = [new Tag("x", "Test", "#000")] };

        _sut.Write(_tempFolder, store);

        var filetagsPath = Path.Combine(_tempFolder, ".filetags");
        filetagsPath.Should().Match(p => File.Exists(p));

        var loaded = _sut.Read(_tempFolder);
        loaded.Tags.Should().HaveCount(1);
    }

    [Fact]
    public void Read_Throws_UnsupportedVersionException_ForUnknownVersion()
    {
        var json = """{"version": 99, "tags": [], "files": {}}""";
        File.WriteAllText(Path.Combine(_tempFolder, ".filetags"), json);

        var act = () => _sut.Read(_tempFolder);

        act.Should().Throw<UnsupportedVersionException>()
            .Which.Version.Should().Be(99);
    }

    [Fact]
    public void Write_OverwritesExistingFile()
    {
        var store1 = new TagStore { Tags = [new Tag("a", "Alpha", "#111")] };
        var store2 = new TagStore { Tags = [new Tag("b", "Beta", "#222")] };

        _sut.Write(_tempFolder, store1);
        _sut.Write(_tempFolder, store2);

        var loaded = _sut.Read(_tempFolder);
        loaded.Tags.Should().HaveCount(1).And.Contain(t => t.Name == "Beta");
    }
}
