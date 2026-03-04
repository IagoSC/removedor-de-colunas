param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$Version,

    [switch]$RequireSignature
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$releaseDir = Join-Path $projectRoot ("release\v" + $Version)

if (-not (Test-Path $releaseDir)) {
    throw "Diretório de release não encontrado: $releaseDir"
}

$expectedExe = Join-Path $releaseDir ("anonimizador_de_csv_v" + $Version + ".exe")
$expectedZip = Join-Path $releaseDir ("anonimizador_de_csv_v" + $Version + ".zip")
$expectedReadme = Join-Path $releaseDir "README.md"
$expectedManifest = Join-Path $releaseDir "manifest.json"
$expectedSums = Join-Path $releaseDir "SHA256SUMS.txt"

$requiredFiles = @($expectedExe, $expectedZip, $expectedReadme, $expectedManifest, $expectedSums)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        throw "Arquivo obrigatório ausente: $file"
    }
}

$sumLines = Get-Content $expectedSums | Where-Object { $_.Trim() -ne "" }
if ($sumLines.Count -eq 0) {
    throw "SHA256SUMS.txt está vazio"
}

$sumMap = @{}
foreach ($line in $sumLines) {
    $parts = $line -split "\s\*", 2
    if ($parts.Count -ne 2) {
        throw "Linha inválida em SHA256SUMS.txt: $line"
    }
    $hash = $parts[0].Trim().ToLower()
    $name = $parts[1].Trim()
    $sumMap[$name] = $hash
}

$filesToCheck = Get-ChildItem -Path $releaseDir -File | Where-Object { $_.Name -ne "SHA256SUMS.txt" }
foreach ($file in $filesToCheck) {
    if (-not $sumMap.ContainsKey($file.Name)) {
        throw "Arquivo sem hash registrado: $($file.Name)"
    }
    $currentHash = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash.ToLower()
    if ($currentHash -ne $sumMap[$file.Name]) {
        throw "Hash divergente para $($file.Name)"
    }
}

if ($RequireSignature) {
    $signature = Get-AuthenticodeSignature -FilePath $expectedExe
    if ($signature.Status -ne 'Valid') {
        throw "Assinatura digital inválida ou ausente em $expectedExe (Status: $($signature.Status))"
    }
}

Write-Host "Validação concluída com sucesso para v$Version"
Write-Host "- Estrutura de arquivos: OK"
Write-Host "- Integridade SHA-256: OK"
if ($RequireSignature) {
    Write-Host "- Assinatura digital: OK"
}
