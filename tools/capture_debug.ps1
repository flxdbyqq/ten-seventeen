Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32f {
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

$outDir = "E:\aiproject\new\shots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function RunWarp($line, $name) {
    Get-Process -Name renpy -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 1
    Start-Process -FilePath "E:\aiproject\new\_sdk\renpy-8.6.1-sdk\renpy.exe" -ArgumentList @("--warp", "game/script.rpy:$line", "E:\aiproject\new")
    $proc = $null
    for ($i = 0; $i -lt 60; $i++) {
        $proc = Get-Process -Name renpy -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
        if ($proc) { break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $proc) { Write-Error "window not found"; return }
    $hwnd = $proc.MainWindowHandle
    [Win32f]::SetWindowPos($hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0041) | Out-Null
    [Win32f]::BringWindowToTop($hwnd) | Out-Null
    [Win32f]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Seconds 3
    $rect = New-Object Win32f+RECT
    [Win32f]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    $w = $rect.Right - $rect.Left
    $h = $rect.Bottom - $rect.Top
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bmp.Size)
    $path = Join-Path $outDir $name
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    Write-Host "saved $path"
    $proc.CloseMainWindow() | Out-Null
    Start-Sleep -Seconds 2
    if (-not $proc.HasExited) { $proc.Kill() }
}

RunWarp 344 "debug_hall.png"
RunWarp 357 "debug_choices.png"
Write-Host "done"
