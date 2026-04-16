namespace FileTagExplorer.Exceptions;

public sealed class UnsupportedVersionException(int version)
    : Exception($".filetags のバージョン {version} はサポートされていません。")
{
    public int Version { get; } = version;
}
