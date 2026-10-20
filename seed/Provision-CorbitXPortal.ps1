<#
 Creates and fills every list behind the Corbit X Journey portal, and uploads the six posters and the voiceover MP3s.
 Needs PnP.PowerShell (Install-Module PnP.PowerShell) and Site Owner rights.

   .\Provision-CorbitXPortal.ps1 -SiteUrl https://yourtenant.sharepoint.com/sites/Intranet

 Safe to re-run: existing lists/columns are kept, and a list that already has items is NOT re-seeded
 (add -Reseed to wipe and refill the seed content).
#>
param(
  [Parameter(Mandatory)][string]$SiteUrl,
  [switch]$Reseed
)
$ErrorActionPreference = 'Stop'
$here   = Split-Path -Parent $MyInvocation.MyCommand.Path
$schema = Get-Content (Join-Path $here '..\src\webparts\corbitXJourney\portal\schema.json') -Raw | ConvertFrom-Json
$seed   = Get-Content (Join-Path $here 'seed.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Connect-PnPOnline -Url $SiteUrl -Interactive

# 1. poster images -> SiteAssets/CorbitX/posters
$null = Resolve-PnPFolder -SiteRelativePath 'SiteAssets/CorbitX/posters'
$null = Resolve-PnPFolder -SiteRelativePath 'SiteAssets/CorbitX/voice/emily'
$webUrl = (Get-PnPWeb).ServerRelativeUrl.TrimEnd('/')
foreach ($row in $seed.Posters) {
  $null = Add-PnPFile -Path (Join-Path $here ("posters\" + $row.ImageFile)) -Folder 'SiteAssets/CorbitX/posters'
  $row | Add-Member -NotePropertyName ImageUrl -NotePropertyValue "$webUrl/SiteAssets/CorbitX/posters/$($row.ImageFile)" -Force
}

# Emily's voiceover (generated MP3s) -> SiteAssets/CorbitX/voice/emily
Get-ChildItem (Join-Path $here 'voice\emily') -Filter *.mp3 | ForEach-Object { $null = Add-PnPFile -Path $_.FullName -Folder 'SiteAssets/CorbitX/voice/emily' }

# 2. lists, columns, items
foreach ($def in $schema.lists) {
  $name = $def.list
  if (-not (Get-PnPList -Identity $name -ErrorAction SilentlyContinue)) { $null = New-PnPList -Title $name -Template GenericList -OnQuickLaunch }
  $cols = @(@{N='Order';T='Number'}, @{N='IsActive';T='Boolean'})
  foreach ($f in $def.fields) {
    $t = switch ($f.t) { 'note' {'Note'} 'lines' {'Note'} 'pairs' {'Note'} 'number' {'Number'} 'bool' {'Boolean'} 'choice' {'Choice'} default {'Text'} }
    $cols += @{N=$f.n; T=$t; C=$f.choices}
  }
  if ($def.kind -eq 'posters') { $cols += @{N='ImageFile'; T='Text'} }
  foreach ($c in $cols) {
    if (Get-PnPField -List $name -Identity $c.N -ErrorAction SilentlyContinue) { continue }
    if ($c.T -eq 'Choice') { $null = Add-PnPField -List $name -DisplayName $c.N -InternalName $c.N -Type Choice -Choices $c.C -AddToDefaultView }
    elseif ($c.T -eq 'Note') { $null = Add-PnPField -List $name -DisplayName $c.N -InternalName $c.N -Type Note -AddToDefaultView; Set-PnPField -List $name -Identity $c.N -Values @{RichText=$false; NumberOfLines=6} }
    else { $null = Add-PnPField -List $name -DisplayName $c.N -InternalName $c.N -Type $c.T -AddToDefaultView }
  }
  Set-PnPField -List $name -Identity 'IsActive' -Values @{DefaultValue='1'}
  if ($def.titleProp) { Set-PnPField -List $name -Identity 'Title' -Values @{Title=$def.titleProp} }

  $existing = (Get-PnPListItem -List $name -PageSize 1 | Measure-Object).Count
  if ($existing -gt 0 -and -not $Reseed) { Write-Host "Kept   $name (already has items)"; continue }
  if ($Reseed) { Get-PnPListItem -List $name -PageSize 500 | ForEach-Object { Remove-PnPListItem -List $name -Identity $_.Id -Force } }
  foreach ($r in $seed.($name)) {
    $v = @{}
    foreach ($p in $r.PSObject.Properties) { $v[$p.Name] = $p.Value }
    $null = Add-PnPListItem -List $name -Values $v
  }
  Write-Host "Seeded $name ($(@($seed.($name)).Count) items)"
}
Write-Host "`nDone. Edit the lists to change the portal. Voiceover MP3s are in SiteAssets/CorbitX/voice/emily/."
