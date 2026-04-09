import "pe"
import "hash"

rule Tool_SharpHound_BloodHound {
    meta:
        description = "Detects SharpHound/BloodHound collector"
        author = "Threat Hunter"
        tool = "BloodHound"
    strings:
        $s1 = "SharpHound" ascii
        $s2 = "BloodHound" ascii
        $s3 = "CollectionMethod" ascii
        $json = "_computers.json" ascii
    condition:
        2 of them
}
