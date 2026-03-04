param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$Version,

    [Parameter(Mandatory = $true)]
    [string]$Thumbprint,

    [string]$CertStoreLocation = "Cert:\CurrentUser\My",

    [string]$TimestampServer = "http://timestamp.digicert.com"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$releaseDir = Join-Path $projectRoot ("release\v" + $Version)
$exePath = Join-Path $releaseDir ("anonimizador_de_csv_v" + $Version + ".exe")

if (-not (Test-Path $exePath)) {
    throw "Executável não encontrado: $exePath"
}

$normalizedThumbprint = ($Thumbprint -replace "\s", "").ToUpperInvariant()
$certPath = Join-Path $CertStoreLocation $normalizedThumbprint

if (-not (Test-Path $certPath)) {
    throw "Certificado não encontrado: $certPath"
}

$cert = Get-Item $certPath

$signature = Set-AuthenticodeSignature -FilePath $exePath -Certificate $cert -TimestampServer $TimestampServer
if ($signature.Status -ne 'Valid') {
    throw "Falha ao assinar executável. Status: $($signature.Status)"
}

Write-Host "Assinatura aplicada com sucesso em: $exePath"
Write-Host "Thumbprint: $normalizedThumbprint"
