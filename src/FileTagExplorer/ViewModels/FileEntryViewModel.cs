using CommunityToolkit.Mvvm.ComponentModel;
using FileTagExplorer.Models;
using System.Collections.ObjectModel;

namespace FileTagExplorer.ViewModels;

public sealed partial class FileEntryViewModel : ObservableObject
{
    public FileEntry Model { get; }
    public string Name => Model.Name;
    public string RelativePath => Model.RelativePath;
    public string Location => System.IO.Path.GetDirectoryName(Model.RelativePath)?.Replace('\\', '/') ?? "/";
    public long Size => Model.Size;
    public DateTime LastModified => Model.LastModified.ToLocalTime();
    public string FullPath => Model.FullPath;

    [ObservableProperty]
    private bool _isSelected;

    public ObservableCollection<TagViewModel> AssignedTags { get; } = [];

    public FileEntryViewModel(FileEntry model, IEnumerable<TagViewModel>? tags = null)
    {
        Model = model;
        if (tags != null)
            foreach (var t in tags)
                AssignedTags.Add(t);
    }

    public bool HasTag(string tagId) =>
        AssignedTags.Any(t => t.Id == tagId);
}
