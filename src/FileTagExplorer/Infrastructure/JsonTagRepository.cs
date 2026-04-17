using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;
using FileTagExplorer.Exceptions;
using FileTagExplorer.Models;

namespace FileTagExplorer.Infrastructure;

public sealed class JsonTagRepository : ITagRepository
{
    private const string FileName = ".filetags";
    private const int SupportedVersion = 1;

    private static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    };

    private static string GetPath(string folderPath) =>
        Path.Combine(folderPath, FileName);

    public TagStore Read(string folderPath)
    {
        var path = GetPath(folderPath);
        if (!File.Exists(path))
            return new TagStore();

        var json = File.ReadAllText(path);
        var store = JsonSerializer.Deserialize<TagStore>(json, Options)
            ?? throw new InvalidOperationException(".filetags のデシリアライズに失敗しました。");

        if (store.Version != SupportedVersion)
            throw new UnsupportedVersionException(store.Version);

        return store;
    }

    public void Write(string folderPath, TagStore store)
    {
        var targetPath = GetPath(folderPath);
        var tmpPath = Path.GetTempFileName();
        try
        {
            var json = JsonSerializer.Serialize(store, Options);
            File.WriteAllText(tmpPath, json);
            File.Move(tmpPath, targetPath, overwrite: true); // アトミック置換 (INV-004)
        }
        finally
        {
            if (File.Exists(tmpPath))
                File.Delete(tmpPath);
        }
    }
}
