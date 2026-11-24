using UnrealBuildTool;

public class UnrealBPBridge : ModuleRules
{
    public UnrealBPBridge(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PrivateDependencyModuleNames.AddRange(new[] { "Json", "JsonUtilities", "MaterialEditor", "RHI" });
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "UnrealEd", "StateTreeModule", "StateTreeEditorModule", "Blutility", "GameplayCameras" });
    }
}
