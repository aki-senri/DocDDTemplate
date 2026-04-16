using CommunityToolkit.Mvvm.ComponentModel;
using FileTagExplorer.Models;
using System.Collections.ObjectModel;

namespace FileTagExplorer.ViewModels;

public sealed partial class FolderNodeViewModel : ObservableObject
{
    public FolderNode Model { get; }
    public string Name => Model.Name;
    public string RelativePath => Model.RelativePath;
    public string FullPath => Model.FullPath;

    [ObservableProperty]
    private bool _isSelected;

    [ObservableProperty]
    private bool _isExpanded;

    public ObservableCollection<FolderNodeViewModel> Children { get; }

    public FolderNodeViewModel(FolderNode model)
    {
        Model = model;
        Children = new ObservableCollection<FolderNodeViewModel>(
            model.Children.Select(c => new FolderNodeViewModel(c)));
        IsExpanded = true;
    }
}
