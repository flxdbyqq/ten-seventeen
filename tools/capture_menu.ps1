Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32c {
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@

Get-Process -Name renpy -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1
Start-Process -FilePath "E:\aiproject\new\_sdk\renpy-8.6.1-sdk\renpy.exe" -ArgumentList "E:\aiproject\new"

$proc = $null
for ($i = 0; $i -lt 60; $i++) {
    $proc = Get-Process -Name renpy -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if ($proc) { break }
    Start-Sleep -Milliseconds 500
}
if (-not $proc) { Write-Error "renpy window not found"; exit 1 }
$hwnd = $proc.MainWindowHandle
[Win32c]::SetWindowPos($hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0041) | Out-Null
[Win32c]::BringWindowToTop($hwnd) | Out-Null
[Win32c]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Seconds 2

$outDir = "E:\aiproject\new\shots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$rect = New-Object Win32c+RECT
[Win32c]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
$w = $rect.Right - $rect.Left
$h = $rect.Bottom - $rect.Top
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bmp.Size)
$path = Join-Path $outDir "main_menu_new.png"
$bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
Write-Host "saved $path ${w}x${h} at $($rect.Left),$($rect.Top)"
Write-Host "pid $($proc.Id)"
