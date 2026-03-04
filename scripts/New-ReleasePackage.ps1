param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$Version,

    [string]$PythonCommand = "python",

    [switch]$Clean,

    [switch]$SkipDependencyInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$mainScript = Join-Path $projectRoot "anonimizador_de_csv.py"
$readmePath = Join-Path $projectRoot "README.md"

if (-not (Test-Path $mainScript)) {
    throw "Arquivo principal não encontrado: $mainScript"
}

if (-not (Test-Path $readmePath)) {
    throw "README não encontrado: $readmePath"
}

Push-Location $projectRoot
try {
    if ($Clean) {
        if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
        if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
    }

    if (-not $SkipDependencyInstall) {
        & $PythonCommand -m pip install --upgrade pip
        & $PythonCommand -m pip install customtkinter chardet dbfread pyinstaller
    }

    & $PythonCommand -m PyInstaller --noconfirm --clean --onefile --windowed --name "anonimizador_de_csv" "anonimizador_de_csv.py"

    $builtExe = Join-Path $projectRoot "dist\anonimizador_de_csv.exe"
    if (-not (Test-Path $builtExe)) {
        throw "Build falhou: executável não encontrado em $builtExe"
    }

    $releaseDir = Join-Path $projectRoot ("release\v" + $Version)
    if (Test-Path $releaseDir) {
        Remove-Item $releaseDir -Recurse -Force
    }
    New-Item -Path $releaseDir -ItemType Directory | Out-Null

    $versionedExeName = "anonimizador_de_csv_v$Version.exe"
    $versionedExePath = Join-Path $releaseDir $versionedExeName
    Copy-Item $builtExe $versionedExePath -Force

    Copy-Item $readmePath (Join-Path $releaseDir "README.md") -Force

    $optionalPolicyFiles = @("DATA_POLICY.md", "SECURITY.md")
    foreach ($fileName in $optionalPolicyFiles) {
        $candidate = Join-Path $projectRoot $fileName
        if (Test-Path $candidate) {
            Copy-Item $candidate (Join-Path $releaseDir $fileName) -Force
        }
    }

    $gitCommit = "not-a-git-repo"
    try {
        $gitCommit = (git rev-parse --short HEAD)
    }
    catch {
        $gitCommit = "unavailable"
    }

    $manifest = [ordered]@{
        appName = "anonimizador_de_csv"
        version = $Version
        builtAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        buildHost = $env:COMPUTERNAME
        sourceCommit = "$gitCommit"
        files = @()
    }

    $filesToPackage = Get-ChildItem -Path $releaseDir -File | Where-Object { $_.Name -notin @("SHA256SUMS.txt") }

    foreach ($file in $filesToPackage) {
        $manifest.files += [ordered]@{
            name = $file.Name
            sizeBytes = $file.Length
        }
    }

    $manifestPath = Join-Path $releaseDir "manifest.json"
    ($manifest | ConvertTo-Json -Depth 5) | Set-Content -Path $manifestPath -Encoding UTF8

    $zipName = "anonimizador_de_csv_v$Version.zip"
    $zipPath = Join-Path $releaseDir $zipName
    $contentForZip = Get-ChildItem -Path $releaseDir -File | Where-Object { $_.Name -ne $zipName }
    Compress-Archive -Path $contentForZip.FullName -DestinationPath $zipPath -Force

    $hashFile = Join-Path $releaseDir "SHA256SUMS.txt"
    if (Test-Path $hashFile) {
        Remove-Item $hashFile -Force
    }

    $hashTargets = Get-ChildItem -Path $releaseDir -File | Where-Object { $_.Name -ne "SHA256SUMS.txt" }
    foreach ($target in $hashTargets) {
        $hash = (Get-FileHash -Path $target.FullName -Algorithm SHA256).Hash.ToLower()
        "$hash *$($target.Name)" | Add-Content -Path $hashFile -Encoding UTF8
    }

    Write-Host "Release criada com sucesso em: $releaseDir"
    Write-Host "- Executável: $versionedExeName"
    Write-Host "- Pacote ZIP: $zipName"
    Write-Host "- Checksums: SHA256SUMS.txt"
}
finally {
    Pop-Location
}
