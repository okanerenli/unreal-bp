#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "EdGraph/EdGraphPin.h"
#include "UnrealBPBridgeLibrary.generated.h"

class UAnimCompositeFactory;
class UEdGraphNode;
class UPreviewMeshCollectionFactory;
class USkeleton;
class UFactory;
class UCameraAsset;
class UStateTreeFactory;
class UUserDefinedStruct;
class UUserDefinedEnum;
class UMaterial;
class UMaterialExpression;
class UMaterialInterface;
class UMaterialInstanceConstant;
class UMaterialExpressionMaterialAttributeLayers;

UCLASS()
class UNREALBPBRIDGE_API UUnrealBPBridgeLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static FString GetEnumEntries(UUserDefinedEnum* Enum);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool EditEnumEntry(UUserDefinedEnum* Enum, const FString& Action, const FString& Entry, const FString& DisplayName);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static FString GetNodeComment(UEdGraphNode* Node);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool SetNodeComment(UEdGraphNode* Node, const FString& Text, bool Visible, bool Pinned);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool ResizeComment(UEdGraphNode* Node, int32 Width, int32 Height);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool SetMaterialLayerStack(UMaterialExpressionMaterialAttributeLayers* Expression, const FString& Json);

    UFUNCTION(BlueprintPure, Category = "Unreal BP Bridge")
    static int32 GetProtocolVersion();

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static FString GetMaterialOutputs(UMaterial* Material, const TArray<FString>& Properties);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool ConnectMaterialOutput(UMaterial* Material, const FString& Property, UMaterialExpression* Expression, const FString& Output);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool DisconnectMaterialOutput(UMaterial* Material, const FString& Property);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static FString GetMaterialDiagnostics(UMaterial* Material);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static FString GetMaterialParameters(UMaterialInterface* Material);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static FString EditMaterialParameter(UMaterialInstanceConstant* Instance, const FString& Action, const FString& Arguments);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static FString GetStructFields(UUserDefinedStruct* Struct);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool EditStructField(UUserDefinedStruct* Struct, const FString& Name, const FEdGraphPinType& Type, const FString& DefaultValue, const FString& RenameFrom);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool DeleteStructField(UUserDefinedStruct* Struct, const FString& Name);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool MoveStructField(UUserDefinedStruct* Struct, const FString& Name, const FString& RelativeTo, bool bAfter);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool SetStructFieldTooltip(UUserDefinedStruct* Struct, const FString& Name, const FString& Tooltip);

    UFUNCTION(BlueprintPure, Category = "Unreal BP Bridge")
    static bool IsDataAssetClassAllowed(UClass* AssetClass);

    UFUNCTION(BlueprintPure, Category = "Unreal BP Bridge")
    static bool IsSoundEffectPresetClassAllowed(UClass* AssetClass);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool ConfigureAnimCompositeFactory(UAnimCompositeFactory* Factory, USkeleton* Skeleton);

    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool ConfigurePreviewMeshCollectionFactory(UPreviewMeshCollectionFactory* Factory, USkeleton* Skeleton);
    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool ConfigurePCGGraphInstanceFactory(UFactory* Factory, UObject* ParentGraph);
    UFUNCTION(BlueprintCallable, Category = "Unreal BP Bridge")
    static bool ConfigureStateTreeFactory(UStateTreeFactory* Factory, UClass* SchemaClass);
    UFUNCTION(BlueprintPure, Category = "Unreal BP Bridge")
    static bool IsConcreteFactoryClass(UClass* AssetClass);
    UFUNCTION(BlueprintPure, Category = "Unreal BP Bridge")
    static bool IsEditorUtilityParentAllowed(UClass* ParentClass);
    UFUNCTION(BlueprintPure, Category = "Unreal BP Bridge")
    static bool HasCameraDirectorClass(UCameraAsset* Asset, UClass* DirectorClass);
};
