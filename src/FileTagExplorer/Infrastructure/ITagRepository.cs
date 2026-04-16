using FileTagExplorer.Models;

namespace FileTagExplorer.Infrastructure;

public interface ITagRepository
{
    /// <summary>folderPath 内の .filetags を読み込む。存在しなければ空の TagStore を返す。</summary>
    TagStore Read(string folderPath);

    /// <summary>folderPath 内の .filetags に書き込む（一時ファイル経由のアトミック置換）。</summary>
    void Write(string folderPath, TagStore store);
}
