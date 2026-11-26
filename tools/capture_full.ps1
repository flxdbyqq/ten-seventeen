Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32g {
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")]
    public static extern bool GetClientRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")]
    public static extern bool ClientToScreen(IntPtr hWnd, ref POINT pt);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    [StructLayout(LayoutKind.Sequential)]
    public struct POINT { public int X; public int Y; }
}
"@

$outDir = "E:\aiproject\new\shots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$scale = 1.5

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
    [Win32g]::SetWindowPos($hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0041) | Out-Null
    [Win32g]::BringWindowToTop($hwnd) | Out-Null
    [Win32g]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Seconds 3

    $cr = New-Object Win32g+RECT
    [Win32g]::GetClientRect($hwnd, [ref]$cr) | Out-Null
    $pt = New-Object Win32g+POINT
    $pt.X = 0
    $pt.Y = 0
    [Win32g]::ClientToScreen($hwnd, [ref]$pt) | Out-Null
    $x = [int]($pt.X * $scale)
    $y = [int]($pt.Y * $scale)
    $w = [int](($cr.Right - $cr.Left) * $scale)
    $h = [int](($cr.Bottom - $cr.Top) * $scale)
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($x, $y, 0, 0, $bmp.Size)
    $path = Join-Path $outDir $name
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    Write-Host "saved $path ${w}x${h} at $x,$y"
    $proc.CloseMainWindow() | Out-Null
    Start-Sleep -Seconds 2
    if (-not $proc.HasExited) { $proc.Kill() }
}

RunWarp 344 "full_hall.png"
RunWarp 357 "full_choices.png"
Write-Host "done"
