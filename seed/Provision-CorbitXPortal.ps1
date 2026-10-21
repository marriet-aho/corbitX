<#
 Sets up everything behind the Corbit X Readiness Centre web part, and locks it so ONLY OWNERS CAN EDIT.
   - creates 25 lists (columns included) and fills them with the current content
   - uploads the 6 posters and the 205 voice clips to SiteAssets/CorbitX
   - gives the site Owners Full Control and everyone else Read-only on every list and on the assets folder

 Needs PnP.PowerShell (Install-Module PnP.PowerShell) and Site Owner rights.

   .\Provision-CorbitXPortal.ps1 -SiteUrl https://<tenant>.sharepoint.com/sites/<site> -OwnerEmail you@yourbank.com

 Safe to re-run: existing lists/columns are kept, and a list that already has items is NOT re-seeded (add -Reseed to wipe and
 refill the seed content). Add -SkipLock to leave permissions alone.
#>
param(
  [Parameter(Mandatory)][string]$SiteUrl,
  [string]$OwnerEmail,
  [switch]$Reseed,
  [switch]$SkipLock
)
$ErrorActionPreference = 'Stop'
$here   = Split-Path -Parent $MyInvocation.MyCommand.Path
$schema = Get-Content (Join-Path $here 'schema.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$seed   = Get-Content (Join-Path $here 'seed.json') -Raw -Encoding UTF8 | ConvertFrom-Json
Connect-PnPOnline -Url $SiteUrl -Interactive

# 1. posters and voice clips -> SiteAssets/CorbitX
$null = Resolve-PnPFolder -SiteRelativePath 'SiteAssets/CorbitX/posters'
$null = Resolve-PnPFolder -SiteRelativePath 'SiteAssets/CorbitX/voice/emily'
$webUrl = (Get-PnPWeb).ServerRelativeUrl.TrimEnd('/')
foreach ($row in $seed.Posters) {
  $null = Add-PnPFile -Path (Join-Path $here ("posters\" + $row.ImageFile)) -Folder 'SiteAssets/CorbitX/posters'
  $row | Add-Member -NotePropertyName ImageUrl -NotePropertyValue "$webUrl/SiteAssets/CorbitX/posters/$($row.ImageFile)" -Force
}
Get-ChildItem (Join-Path $here 'voice\emily') -Filter *.mp3 | ForEach-Object { $null = Add-PnPFile -Path $_.FullName -Folder 'SiteAssets/CorbitX/voice/emily' }
Write-Host "Uploaded posters and voice clips"

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
  $label = if ($def.titleLabel) { $def.titleLabel } elseif ($def.titleProp) { $def.titleProp } else { $null }
  if ($label) { Set-PnPField -List $name -Identity 'Title' -Values @{Title=$label} }

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

# 3. owner-only editing: Owners = Full Control, everyone else = Read
if (-not $SkipLock) {
  $owners   = Get-PnPGroup -AssociatedOwnerGroup
  $members  = Get-PnPGroup -AssociatedMemberGroup
  $visitors = Get-PnPGroup -AssociatedVisitorGroup
  foreach ($def in $schema.lists) {
    $name = $def.list
    Set-PnPList -Identity $name -BreakRoleInheritance -CopyRoleAssignments:$false -ClearSubscopes
    Set-PnPListPermission -Identity $name -Group $owners   -AddRole 'Full Control'
    Set-PnPListPermission -Identity $name -Group $members  -AddRole 'Read'
    Set-PnPListPermission -Identity $name -Group $visitors -AddRole 'Read'
    if ($OwnerEmail) { Set-PnPListPermission -Identity $name -User $OwnerEmail -AddRole 'Full Control' }
  }
  try {
    Set-PnPFolderPermission -List 'SiteAssets' -Identity 'SiteAssets/CorbitX' -Group $owners -AddRole 'Full Control' -ClearExisting
    Set-PnPFolderPermission -List 'SiteAssets' -Identity 'SiteAssets/CorbitX' -Group $members  -AddRole 'Read'
    Set-PnPFolderPermission -List 'SiteAssets' -Identity 'SiteAssets/CorbitX' -Group $visitors -AddRole 'Read'
    if ($OwnerEmail) { Set-PnPFolderPermission -List 'SiteAssets' -Identity 'SiteAssets/CorbitX' -User $OwnerEmail -AddRole 'Full Control' }
  } catch { Write-Warning "Could not lock SiteAssets/CorbitX: $($_.Exception.Message)" }
  Write-Host "`nLocked: only Owners$(if ($OwnerEmail) { " and $OwnerEmail" }) can edit; everyone else can only read."
}
Write-Host "`nDone. Edit the lists to change the page. Also restrict who can edit the page itself (see README, step 4)."
