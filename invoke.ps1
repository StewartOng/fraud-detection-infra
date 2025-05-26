# invoke-lambda.ps1

$functionName = "fraud-checker"
$payloadFile = "event.json"
$outputFile = "output.json"

aws lambda invoke `
    --function-name $functionName `
    --payload file://$payloadFile `
    --cli-binary-format raw-in-base64-out `
    $outputFile

Write-Output "Lambda response written to $outputFile:"
Get-Content $outputFile
