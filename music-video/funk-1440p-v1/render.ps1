param(
 [Parameter(Mandatory=$true)][string]$Audio,
 [string]$Output = (Join-Path $PSScriptRoot '../ADV-funk-revised-1440p.mp4')
)
$audioFile = (Resolve-Path -LiteralPath $Audio).Path
$outputFile = [System.IO.Path]::GetFullPath($Output)
Push-Location $PSScriptRoot
try {
 & ffmpeg -hide_banner -y -f concat -safe 0 -i scenes.txt -i $audioFile -vf 'fps=30,ass=lyrics.ass' -t 257.9273 -c:v h264_nvenc -preset p5 -cq 18 -b:v 0 -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart $outputFile
 if ($LASTEXITCODE -ne 0) { throw 'FFmpeg render failed' }
} finally { Pop-Location }
