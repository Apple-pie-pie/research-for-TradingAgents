param(
    [switch]$Install,
    [switch]$Help,
    [switch]$Analyze,
    [switch]$Checkpoint,
    [switch]$ClearCheckpoints
)

$ErrorActionPreference = "Stop"

$deployDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceDir = Join-Path $deployDir "..\源代码"
$venvDir = Join-Path $deployDir ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path $sourceDir)) {
    throw "找不到源代码目录: $sourceDir"
}

Push-Location $deployDir
try {
    if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
        Copy-Item ".env.example" ".env"
    }

    if ($Install -or -not (Test-Path $pythonExe)) {
        python -m venv $venvDir
        & $pythonExe -m pip install --upgrade pip
        & $pythonExe -m pip install $sourceDir
    }

    $caBundle = & $pythonExe (Join-Path $deployDir "prepare_runtime.py")
    if ($caBundle) {
        $env:SSL_CERT_FILE = $caBundle
        $env:REQUESTS_CA_BUNDLE = $caBundle
        $env:CURL_CA_BUNDLE = $caBundle
    }

    $env:PYTHONUTF8 = "1"

    if ($Help) {
        & $pythonExe -m cli.main --help
        exit $LASTEXITCODE
    }

    $arguments = @("-m", "cli.main")

    if ($Analyze) {
        $arguments += "analyze"
    }
    if ($Checkpoint) {
        $arguments += "--checkpoint"
    }
    if ($ClearCheckpoints) {
        $arguments += "--clear-checkpoints"
    }

    & $pythonExe @arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}