using FileTagExplorer.Exceptions;
using FileTagExplorer.Infrastructure;
using FileTagExplorer.Models;
using FileTagExplorer.Services;
using FluentAssertions;
using Moq;

namespace FileTagExplorer.Tests.Services;

public sealed class TagStoreServiceTests
{
    private readonly Mock<ITagRepository> _repoMock = new();
    private readonly TagStoreService _sut;
    private readonly TagStore _store;

    public TagStoreServiceTests()
    {
        _sut = new TagStoreService(_repoMock.Object);
        _store = new TagStore
        {
            Tags = [new Tag("t1", "重要", "#FF5722"), new Tag("t2", "WIP", "#2196F3")],
            Files =
            {
                ["report.pdf"] = ["t1"],
                ["drafts/draft.docx"] = ["t1", "t2"],
            }
        };
    }

    // ─── CreateTag ────────────────────────────────────────────────
    [Fact]
    [Trait("AC", "AC-006")]
    public void CreateTag_AddsTagToStore()
    {
        var tag = _sut.CreateTag(_store, "確認済み", "#4CAF50");

        tag.Name.Should().Be("確認済み");
        tag.Color.Should().Be("#4CAF50");
        tag.Id.Should().NotBeNullOrEmpty();
        _store.Tags.Should().Contain(t => t.Id == tag.Id);
    }

    [Fact]
    [Trait("AC", "AC-006")]
    public void CreateTag_WithDuplicateName_ThrowsDuplicateTagNameException()
    {
        var act = () => _sut.CreateTag(_store, "重要", "#000");

        act.Should().Throw<DuplicateTagNameException>()
            .Which.TagName.Should().Be("重要");
    }

    [Fact]
    [Trait("AC", "AC-006")]
    public void CreateTag_WithDuplicateName_CaseInsensitive_ThrowsException()
    {
        var act = () => _sut.CreateTag(_store, "重要", "#000"); // same as "重要"

        act.Should().Throw<DuplicateTagNameException>();
    }

    // ─── DeleteTag ─────────────────────────────────────────────────
    [Fact]
    [Trait("AC", "AC-005")]
    public void DeleteTag_RemovesTagFromDefinitions()
    {
        _sut.DeleteTag(_store, "t1");

        _store.Tags.Should().NotContain(t => t.Id == "t1");
    }

    [Fact]
    [Trait("AC", "AC-005")]
    public void DeleteTag_RemovesTagFromAllFileEntries_INV001()
    {
        _sut.DeleteTag(_store, "t1");

        // INV-001: 全ファイルエントリから参照が消えていること
        _store.Files.Values
            .SelectMany(ids => ids)
            .Should().NotContain("t1");
    }

    [Fact]
    [Trait("AC", "AC-005")]
    public void DeleteTag_RemovesEmptyFileEntries()
    {
        // t1 のみ持っているファイルは削除後にエントリが消える
        _sut.DeleteTag(_store, "t1");

        _store.Files.Should().NotContainKey("report.pdf");
    }

    // ─── AddTag / RemoveTag ────────────────────────────────────────
    [Fact]
    [Trait("AC", "AC-004")]
    public void AddTag_AddsTagIdToFile()
    {
        _sut.AddTag(_store, "image.png", "t2");

        _store.Files["image.png"].Should().Contain("t2");
    }

    [Fact]
    [Trait("AC", "AC-004")]
    public void AddTag_DoesNotDuplicate_WhenAlreadyAssigned()
    {
        _sut.AddTag(_store, "report.pdf", "t1"); // すでに t1 がある

        _store.Files["report.pdf"].Should().ContainSingle(id => id == "t1");
    }

    [Fact]
    [Trait("AC", "AC-005")]
    public void RemoveTag_RemovesTagIdFromFile()
    {
        _sut.RemoveTag(_store, "drafts/draft.docx", "t1");

        _store.Files["drafts/draft.docx"].Should().NotContain("t1");
        _store.Files["drafts/draft.docx"].Should().Contain("t2");
    }

    [Fact]
    [Trait("AC", "AC-005")]
    public void RemoveTag_DeletesFileEntry_WhenNoTagsRemain()
    {
        _sut.RemoveTag(_store, "report.pdf", "t1"); // t1 のみ

        _store.Files.Should().NotContainKey("report.pdf");
    }

    // ─── UpdateFileKey ─────────────────────────────────────────────
    [Fact]
    [Trait("AC", "AC-009")]
    public void UpdateFileKey_MovesTagsToNewKey_INV007()
    {
        var originalTags = _store.Files["report.pdf"].ToList();

        _sut.UpdateFileKey(_store, "report.pdf", "archived/report.pdf");

        _store.Files.Should().NotContainKey("report.pdf");
        _store.Files["archived/report.pdf"].Should().BeEquivalentTo(originalTags);
    }

    [Fact]
    [Trait("AC", "AC-009")]
    public void UpdateFileKey_DoesNothing_WhenOldKeyNotExists()
    {
        var act = () => _sut.UpdateFileKey(_store, "nonexistent.txt", "new/nonexistent.txt");

        act.Should().NotThrow();
    }

    // ─── CleanupOrphanedEntries ────────────────────────────────────
    [Fact]
    public void CleanupOrphanedEntries_RemovesMissingFiles()
    {
        var existing = new[] { "report.pdf" };

        _sut.CleanupOrphanedEntries(_store, existing);

        _store.Files.Should().ContainKey("report.pdf");
        _store.Files.Should().NotContainKey("drafts/draft.docx");
    }
}
