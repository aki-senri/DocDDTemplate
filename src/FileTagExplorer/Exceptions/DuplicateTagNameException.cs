namespace FileTagExplorer.Exceptions;

public sealed class DuplicateTagNameException(string name)
    : Exception($"同名のタグが既に存在します: {name}")
{
    public string TagName { get; } = name;
}
