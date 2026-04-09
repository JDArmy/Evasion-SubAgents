rule Bloodhound_SharpHound_v11 : HKTL RECO TOOL  {
    meta:
        description = "Detects Sharphound PS wrapper"
        author = "Emanuele De Lucia"
        tlp = "white"
    strings:
        $s1 = "function Invoke-BloodHound"
        $s2 = "Runs the BloodHound C# Ingestor using reflection."
        $s3 = "$Assembly.GetType(\"Sharphound2.Sharphound\").GetMethod(\"InvokeBloodHound\")"
    condition:
        3 of ($s*)
}
