Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32k {
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT pt);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
}
"@

$outDir = "E:\aiproject\new\shots"
$scale = 1.5

function Capture($hwnd, $name) {
    $cr = New-Object Win32k+RECT
    [Win32k]::GetClientRect($hwnd, [ref]$cr) | Out-Null
    $pt = New-Object Win32k+POINT
    $pt.X = 0; $pt.Y = 0
    [Win32k]::ClientToScreen($hwnd, [ref]$pt) | Out-Null
    $x = [int]($pt.X * $scale); $y = [int]($pt.Y * $scale)
    $w = [int](($cr.Right - $cr.Left) * $scale); $h = [int](($cr.Bottom - $cr.Top) * $scale)
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($x, $y, 0, 0, $bmp.Size)
    $path = Join-Path $outDir $name
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    Write-Host "saved $path"
}

Get-Process -Name renpy -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1
Start-Process -FilePath "E:\aiproject\new\_sdk\renpy-8.6.1-sdk\renpy.exe" -ArgumentList @("--warp", "game/script.rpy:136", "E:\aiproject\new")
$proc = $null
for ($i = 0; $i -lt 60; $i++) {
    $proc = Get-Process -Name renpy -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if ($proc) { break }
    Start-Sleep -Milliseconds 500
}
if (-not $proc) { Write-Error "window not found"; exit 1 }
$hwnd = $proc.MainWindowHandle
[Win32k]::SetWindowPos($hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0041) | Out-Null
[Win32k]::BringWindowToTop($hwnd) | Out-Null
$ws = New-Object -ComObject WScript.Shell
$ws.AppActivate($proc.Id) | Out-Null
Start-Sleep -Seconds 3

# 点标题栏，只给窗口焦点，不推进对话
$cr = New-Object Win32k+RECT
[Win32k]::GetClientRect($hwnd, [ref]$cr) | Out-Null
$pt = New-Object Win32k+POINT; $pt.X = 0; $pt.Y = 0
[Win32k]::ClientToScreen($hwnd, [ref]$pt) | Out-Null
[Win32k]::SetCursorPos([int]($pt.X + 300), [int]($pt.Y - 12)) | Out-Null
[Win32k]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
[Win32k]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Seconds 1

# ESC
[Win32k]::keybd_event(0x1B, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 100
[Win32k]::keybd_event(0x1B, 0, 2, [UIntPtr]::Zero)
Start-Sleep -Seconds 2
Capture $hwnd "menu_game.png"

$proc.CloseMainWindow() | Out-Null
Start-Sleep -Seconds 2
if (-not $proc.HasExited) { $proc.Kill() }
Write-Host "done"
