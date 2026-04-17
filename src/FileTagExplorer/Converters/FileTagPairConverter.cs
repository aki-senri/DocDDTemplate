using System.Globalization;
using System.Windows.Data;
using FileTagExplorer.ViewModels;

namespace FileTagExplorer.Converters;

public sealed class FileTagPairConverter : IMultiValueConverter
{
    public static readonly FileTagPairConverter Instance = new();

    public object? Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
    {
        if (values is [FileEntryViewModel file, TagViewModel tag])
            return (file, tag);
        return null;
    }

    public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}
