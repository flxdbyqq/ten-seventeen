Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32b {
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
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
[Win32b]::SetWindowPos($hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0041) | Out-Null
[Win32b]::BringWindowToTop($hwnd) | Out-Null
[Win32b]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Seconds 2

$outDir = "E:\aiproject\new\shots"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Capture($path) {
    $rect = New-Object Win32b+RECT
    [Win32b]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    $w = $rect.Right - $rect.Left
    $h = $rect.Bottom - $rect.Top
    if ($w -le 0 -or $h -le 0) { Write-Error "bad rect"; return }
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bmp.Size)
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    Write-Host "saved $path ${w}x${h}"
}

Capture (Join-Path $outDir "main_menu_clean.png")

# Click the empty centre to focus the game window, then Tab+Enter to start.
[Win32b]::SetCursorPos(640, 380) | Out-Null
[Win32b]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
[Win32b]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1200
for ($i = 0; $i -lt 6; $i++) {
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Start-Sleep -Milliseconds 800
}
Start-Sleep -Seconds 3
Capture (Join-Path $outDir "hall_clean.png")

$proc.CloseMainWindow() | Out-Null
Start-Sleep -Seconds 2
if (-not $proc.HasExited) { $proc.Kill() }
Write-Host "done"
