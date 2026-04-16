using CommunityToolkit.Mvvm.ComponentModel;
using FileTagExplorer.Models;

namespace FileTagExplorer.ViewModels;

public sealed partial class TagViewModel : ObservableObject
{
    public Tag Model { get; }
    public string Id => Model.Id;
    public string Name => Model.Name;
    public string Color => Model.Color;

    [ObservableProperty]
    private bool _isFilterActive;

    public TagViewModel(Tag model)
    {
        Model = model;
    }
}
