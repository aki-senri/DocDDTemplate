using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;

namespace FileTagExplorer.Views;

public partial class TagEditorDialog : Window
{
    public string TagName { get; private set; } = "";
    public string TagColor { get; private set; } = "#9E9E9E";

    private static readonly string[] PredefinedColors =
    [
        "#F44336", "#E91E63", "#9C27B0", "#673AB7",
        "#3F51B5", "#2196F3", "#00BCD4", "#009688",
        "#4CAF50", "#8BC34A", "#FFC107", "#FF9800",
        "#FF5722", "#795548", "#9E9E9E", "#607D8B",
    ];

    public TagEditorDialog(string? initialName = null, string? initialColor = null)
    {
        InitializeComponent();

        TagNameBox.Text = initialName ?? "";
        TagColor = initialColor ?? PredefinedColors[5]; // デフォルト: ブルー

        BuildColorPicker();
        UpdatePreview();

        Loaded += (_, _) =>
        {
            TagNameBox.Focus();
            TagNameBox.SelectAll();
        };
    }

    private void BuildColorPicker()
    {
        foreach (var hex in PredefinedColors)
        {
            var brush = new SolidColorBrush(
                (Color)ColorConverter.ConvertFromString(hex));

            var btn = new Button
            {
                Width = 28, Height = 28,
                Margin = new Thickness(3),
                Background = brush,
                BorderBrush = hex == TagColor
                    ? Brushes.Black : Brushes.Transparent,
                BorderThickness = new Thickness(2),
                ToolTip = hex,
                Tag = hex,
            };
            btn.Click += ColorButton_Click;
            ColorPanel.Items.Add(btn);
        }
    }

    private void ColorButton_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button btn) return;
        TagColor = btn.Tag?.ToString() ?? "#9E9E9E";

        // 選択状態の枠線を更新
        foreach (Button b in ColorPanel.Items)
            b.BorderBrush = b.Tag?.ToString() == TagColor
                ? Brushes.Black : Brushes.Transparent;

        UpdatePreview();
    }

    private void UpdatePreview()
    {
        var brush = new SolidColorBrush(
            (Color)ColorConverter.ConvertFromString(TagColor));
        PreviewBorder.Background = brush;
        PreviewText.Text = TagNameBox.Text.Length > 0 ? TagNameBox.Text : "プレビュー";
    }

    private void TagNameBox_KeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Enter) TryConfirm();
    }

    private void OkButton_Click(object sender, RoutedEventArgs e) => TryConfirm();

    private void TryConfirm()
    {
        var name = TagNameBox.Text.Trim();
        if (name.Length == 0)
        {
            MessageBox.Show("タグ名を入力してください。", "入力エラー",
                MessageBoxButton.OK, MessageBoxImage.Warning);
            TagNameBox.Focus();
            return;
        }
        TagName = name;
        DialogResult = true;
        Close();
    }
}
