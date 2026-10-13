# ============================================
#  Inkscape 批量导出脚本（A 加装线）
#  用途：把当前目录所有 SVG 批量导出为 PNG + PDF
#  用法：在含 SVG 的文件夹打开 PowerShell，运行：
#        powershell -ExecutionPolicy Bypass -File "D:\DesignTools\batch-export.ps1"
# ============================================

# ---- 可调参数 ----
$inkscape  = "D:\DesignTools\Inkscape\bin\inkscape.com"   # Inkscape 可执行文件
$widthPx   = 2000      # PNG 导出宽度（像素）。印刷建议 3000，网页 1000-2000
$dpi       = 300       # PDF 分辨率
$exportPng = $true     # 是否导出 PNG
$exportPdf = $true     # 是否导出 PDF

# ---- 主逻辑 ----
if (-not (Test-Path $inkscape)) {
    Write-Output "错误：找不到 Inkscape，请检查路径：$inkscape"
    Write-Output "若安装在其他位置，请修改本脚本顶部的 `$inkscape 变量。"
    exit 1
}

$svgs = Get-ChildItem -Filter *.svg
if ($svgs.Count -eq 0) {
    Write-Output "当前目录没有 SVG 文件。"
    exit 0
}

Write-Output "找到 $($svgs.Count) 个 SVG，开始处理..."
Write-Output "----------------------------------------"

$ok = 0
$fail = 0

foreach ($f in $svgs) {
    $base = $f.BaseName
    try {
        if ($exportPng) {
            & $inkscape $f.FullName --export-filename="$pwd\$base.png" --export-width=$widthPx 2>$null
        }
        if ($exportPdf) {
            & $inkscape $f.FullName --export-filename="$pwd\$base.pdf" --export-area-drawing 2>$null
        }
        Write-Output "OK   $($f.Name)"
        $ok++
    } catch {
        Write-Output "FAIL $($f.Name)"
        $fail++
    }
}

Write-Output "----------------------------------------"
Write-Output "完成：成功 $ok 个，失败 $fail 个"
Write-Output "产物目录：$pwd"
