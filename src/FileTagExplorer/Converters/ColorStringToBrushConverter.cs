using System.Globalization;
using System.Windows.Data;
using System.Windows.Media;

namespace FileTagExplorer.Converters;

[ValueConversion(typeof(string), typeof(Brush))]
public sealed class ColorStringToBrushConverter : IValueConverter
{
    public static readonly ColorStringToBrushConverter Instance = new();

    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is string colorStr)
        {
            try
            {
                var color = (Color)ColorConverter.ConvertFromString(colorStr);
                return new SolidColorBrush(color);
            }
            catch { /* 無効な色文字列はグレーにフォールバック */ }
        }
        return Brushes.Gray;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}
