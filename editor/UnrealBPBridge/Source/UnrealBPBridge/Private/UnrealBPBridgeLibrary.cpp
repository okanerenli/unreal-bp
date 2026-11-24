#include "UnrealBPBridgeLibrary.h"
#include "EdGraphNode_Comment.h"
#include "EdGraph/EdGraph.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "ScopedTransaction.h"
#include "Animation/Skeleton.h"
#include "Factories/AnimCompositeFactory.h"
#include "Factories/PreviewMeshCollectionFactory.h"
#include "Engine/DataAsset.h"
#include "Core/CameraAsset.h"
#include "Core/CameraDirector.h"
#include "EditorUtilityWidget.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "UObject/UObjectGlobals.h"
#include "StateTreeFactory.h"
#include "StateTreeSchema.h"
#include "Sound/SoundEffectSource.h"
#include "Sound/SoundEffectSubmix.h"
#include "Factories/Factory.h"
#include "UObject/UnrealType.h"
#include "UObject/Class.h"
#include "UObject/Stack.h"
#include "Modules/ModuleManager.h"
#include "Kismet2/StructureEditorUtils.h"
#include "Kismet2/EnumEditorUtils.h"
#include "UserDefinedStructure/UserDefinedStructEditorData.h"
#include "Serialization/JsonSerializer.h"
#include "Materials/Material.h"
#include "Materials/MaterialExpression.h"
#include "Materials/MaterialInstanceConstant.h"
#include "MaterialExpressionIO.h"
#include "Materials/MaterialParameters.h"
#include "Engine/Texture.h"
#include "MaterialEditingLibrary.h"
#include "MaterialShared.h"
#include "RHI.h"
#include "JsonObjectConverter.h"
#include "Materials/MaterialExpressionMaterialAttributeLayers.h"
#include "Materials/MaterialFunctionInterface.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, UnrealBPBridge)

int32 UUnrealBPBridgeLibrary::GetProtocolVersion()
{
    return 16;
}

FString UUnrealBPBridgeLibrary::GetEnumEntries(UUserDefinedEnum* Enum)
{
    if (!Enum)
    {
        return TEXT("{\"error\":\"GetEnumEntries requires a UserDefinedEnum\"}");
    }
    TArray<TSharedPtr<FJsonValue>> Entries;
    // UserDefinedEnum reserves its final entry for the generated MAX sentinel.
    for (int32 Index = 0; Index < Enum->NumEnums() - 1; ++Index)
    {
        TSharedRef<FJsonObject> Value = MakeShared<FJsonObject>();
        Value->SetStringField(TEXT("id"), Enum->GetNameStringByIndex(Index));
        Value->SetStringField(TEXT("display_name"), Enum->GetDisplayNameTextByIndex(Index).ToString());
        Value->SetNumberField(TEXT("value"), Enum->GetValueByIndex(Index));
        Entries.Add(MakeShared<FJsonValueObject>(Value));
    }
    FString Result;
    FJsonSerializer::Serialize(Entries, TJsonWriterFactory<>::Create(&Result));
    return Result;
}

bool UUnrealBPBridgeLibrary::EditEnumEntry(UUserDefinedEnum* Enum, const FString& Action, const FString& Entry, const FString& DisplayName)
{
    auto Fail = [&Action, &Entry](const FString& Reason)
    {
        FFrame::KismetExecutionMessage(*FString::Printf(TEXT("EditEnumEntry %s %s: %s"), *Action, *Entry, *Reason), ELogVerbosity::Error);
        return false;
    };
    if (!Enum)
    {
        return Fail(TEXT("Expected a UserDefinedEnum asset"));
    }
    if (Action != TEXT("add") && Action != TEXT("rename") && Action != TEXT("delete"))
    {
        return Fail(TEXT("Action must be add, rename or delete"));
    }
    int32 Index = INDEX_NONE;
    if (Action != TEXT("add"))
    {
        for (int32 Candidate = 0; Candidate < Enum->NumEnums() - 1; ++Candidate)
        {
            if (Enum->GetNameStringByIndex(Candidate) == Entry)
            {
                Index = Candidate;
                break;
            }
        }
        if (Index == INDEX_NONE)
        {
            return Fail(TEXT("Entry id not found; use an exact id from GetEnumEntries"));
        }
    }
    const FText Name = FText::FromString(DisplayName);
    if (Action != TEXT("delete") && !FEnumEditorUtils::IsEnumeratorDisplayNameValid(Enum, Index, Name))
    {
        return Fail(TEXT("Display name is empty, reserved or already used"));
    }
    const FScopedTransaction Transaction(NSLOCTEXT("UnrealBPBridge", "EditEnumEntry", "Edit enum entry"));
    const int32 CountBefore = Enum->NumEnums();
    if (Action == TEXT("delete"))
    {
        FEnumEditorUtils::RemoveEnumeratorFromUserDefinedEnum(Enum, Index);
        if (Enum->NumEnums() != CountBefore - 1)
        {
            return Fail(TEXT("Unreal did not remove the entry"));
        }
        return true;
    }
    if (Action == TEXT("add"))
    {
        FEnumEditorUtils::AddNewEnumeratorForUserDefinedEnum(Enum);
        if (Enum->NumEnums() != CountBefore + 1)
        {
            return Fail(TEXT("Unreal did not add the entry"));
        }
        Index = Enum->NumEnums() - 2;
    }
    if (!FEnumEditorUtils::SetEnumeratorDisplayName(Enum, Index, Name))
    {
        return Fail(TEXT("Display-name edit failed; inspect current entries before resuming"));
    }
    return true;
}

FString UUnrealBPBridgeLibrary::GetNodeComment(UEdGraphNode* Node)
{
    if (!Node)
    {
        return TEXT("{\"error\":\"GetNodeComment requires a graph node\"}");
    }
    TSharedRef<FJsonObject> Value = MakeShared<FJsonObject>();
    Value->SetStringField(TEXT("text"), Node->NodeComment);
    Value->SetBoolField(TEXT("visible"), Node->bCommentBubbleVisible);
    Value->SetBoolField(TEXT("pinned"), Node->bCommentBubblePinned);
    if (UEdGraphNode_Comment* Comment = Cast<UEdGraphNode_Comment>(Node))
    {
        Value->SetNumberField(TEXT("width"), Comment->NodeWidth);
        Value->SetNumberField(TEXT("height"), Comment->NodeHeight);
    }
    FString Result;
    FJsonSerializer::Serialize(Value, TJsonWriterFactory<>::Create(&Result));
    return Result;
}

bool UUnrealBPBridgeLibrary::SetNodeComment(UEdGraphNode* Node, const FString& Text, bool Visible, bool Pinned)
{
    UBlueprint* Blueprint = Node ? FBlueprintEditorUtils::FindBlueprintForNode(Node) : nullptr;
    if (!Blueprint)
    {
        FFrame::KismetExecutionMessage(TEXT("SetNodeComment requires a Blueprint graph node"), ELogVerbosity::Error);
        return false;
    }
    const FScopedTransaction Transaction(NSLOCTEXT("UnrealBPBridge", "SetNodeComment", "Edit node comment"));
    Node->Modify();
    Node->OnUpdateCommentText(Text);
    Node->bCommentBubbleVisible = Visible;
    Node->bCommentBubblePinned = Pinned;
    Node->OnCommentBubbleToggled(Visible);
    Node->GetGraph()->NotifyGraphChanged();
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    return true;
}

bool UUnrealBPBridgeLibrary::ResizeComment(UEdGraphNode* Node, int32 Width, int32 Height)
{
    UEdGraphNode_Comment* Comment = Cast<UEdGraphNode_Comment>(Node);
    UBlueprint* Blueprint = Comment ? FBlueprintEditorUtils::FindBlueprintForNode(Comment) : nullptr;
    if (!Blueprint || Width <= 0 || Height <= 0)
    {
        FFrame::KismetExecutionMessage(TEXT("ResizeComment requires a Blueprint comment node and positive dimensions"), ELogVerbosity::Error);
        return false;
    }
    const FScopedTransaction Transaction(NSLOCTEXT("UnrealBPBridge", "ResizeComment", "Resize comment"));
    Comment->Modify();
    Comment->ResizeNode(FVector2f(Width, Height));
    Comment->GetGraph()->NotifyGraphChanged();
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    return true;
}

FString UUnrealBPBridgeLibrary::GetStructFields(UUserDefinedStruct* Struct)
{
    if (!Struct)
    {
        return TEXT("{\"error\":\"GetStructFields requires a UserDefinedStruct\"}");
    }
    TArray<TSharedPtr<FJsonValue>> Fields;
    for (const FStructVariableDescription& Field : FStructureEditorUtils::GetVarDesc(Struct))
    {
        TSharedRef<FJsonObject> Value = MakeShared<FJsonObject>();
        Value->SetStringField(TEXT("name"), Field.FriendlyName);
        Value->SetStringField(TEXT("guid"), Field.VarGuid.ToString());
        Value->SetStringField(TEXT("category"), Field.ToPinType().PinCategory.ToString());
        Value->SetStringField(TEXT("subcategory"), Field.ToPinType().PinSubCategory.ToString());
        Value->SetStringField(TEXT("default"), Field.DefaultValue);
        Value->SetStringField(TEXT("tooltip"), FStructureEditorUtils::GetVariableTooltip(Struct, Field.VarGuid));
        const FEdGraphPinType Type = Field.ToPinType();
        FString TypeText;
        FEdGraphPinType::StaticStruct()->ExportText(TypeText, &Type, nullptr, Struct, PPF_None, nullptr);
        Value->SetStringField(TEXT("pin_type"), TypeText);
        Value->SetStringField(TEXT("type_object"), GetPathNameSafe(Type.PinSubCategoryObject.Get()));
        Value->SetStringField(TEXT("container"), Type.ContainerType == EPinContainerType::Array ? TEXT("array")
            : Type.ContainerType == EPinContainerType::Set ? TEXT("set")
            : Type.ContainerType == EPinContainerType::Map ? TEXT("map") : TEXT("none"));
        if (Type.ContainerType == EPinContainerType::Map)
        {
            Value->SetStringField(TEXT("value_category"), Type.PinValueType.TerminalCategory.ToString());
            Value->SetStringField(TEXT("value_subcategory"), Type.PinValueType.TerminalSubCategory.ToString());
            Value->SetStringField(TEXT("value_type_object"), GetPathNameSafe(Type.PinValueType.TerminalSubCategoryObject.Get()));
        }
        Fields.Add(MakeShared<FJsonValueObject>(Value));
    }
    FString Result;
    FJsonSerializer::Serialize(Fields, TJsonWriterFactory<>::Create(&Result));
    return Result;
}

bool UUnrealBPBridgeLibrary::EditStructField(UUserDefinedStruct* Struct, const FString& Name, const FEdGraphPinType& Type, const FString& DefaultValue, const FString& RenameFrom)
{
    auto Fail = [&Name](const FString& Reason)
    {
        FFrame::KismetExecutionMessage(*FString::Printf(TEXT("EditStructField %s: %s"), *Name, *Reason), ELogVerbosity::Error);
        return false;
    };
    if (!Struct || Name.IsEmpty())
    {
        return Fail(TEXT("requires a UserDefinedStruct and a nonempty field name"));
    }
    const FString Source = RenameFrom.IsEmpty() ? Name : RenameFrom;
    const FStructVariableDescription* Existing = FStructureEditorUtils::GetVarDesc(Struct).FindByPredicate(
        [&Source](const FStructVariableDescription& Field) { return Field.FriendlyName == Source; });
    if (!RenameFrom.IsEmpty() && !Existing)
    {
        return Fail(TEXT("rename source does not exist"));
    }
    if ((!Existing || Source != Name) && !FStructureEditorUtils::IsUniqueVariableFriendlyName(Struct, Name))
    {
        return Fail(TEXT("destination name already exists"));
    }
    FString TypeError;
    if (!FStructureEditorUtils::CanHaveAMemberVariableOfType(Struct, Type, &TypeError))
    {
        return Fail(TypeError);
    }
    FGuid Guid;
    if (Existing)
    {
        Guid = Existing->VarGuid;
        if (Existing->ToPinType() != Type && !FStructureEditorUtils::ChangeVariableType(Struct, Guid, Type))
        {
            return Fail(TEXT("type change failed"));
        }
    }
    else
    {
        if (!FStructureEditorUtils::AddVariable(Struct, Type))
        {
            return Fail(TEXT("field creation failed"));
        }
        Guid = FStructureEditorUtils::GetVarDesc(Struct).Last().VarGuid;
    }
    if (FStructureEditorUtils::GetVariableFriendlyName(Struct, Guid) != Name
        && !FStructureEditorUtils::RenameVariable(Struct, Guid, Name))
    {
        return Fail(TEXT("rename failed"));
    }
    if (FStructureEditorUtils::GetVarDescByGuid(Struct, Guid)->DefaultValue != DefaultValue
        && !FStructureEditorUtils::ChangeVariableDefaultValue(Struct, Guid, DefaultValue))
    {
        return Fail(TEXT("default value change failed; earlier changes remain applied"));
    }
    return true;
}

bool UUnrealBPBridgeLibrary::DeleteStructField(UUserDefinedStruct* Struct, const FString& Name)
{
    if (Struct)
    {
        const auto& Fields = FStructureEditorUtils::GetVarDesc(Struct);
        const FStructVariableDescription* Field = Fields.FindByPredicate(
            [&Name](const FStructVariableDescription& Item) { return Item.FriendlyName == Name; });
        if (Field && Fields.Num() > 1)
        {
            const FGuid Guid = Field->VarGuid;
            if (FStructureEditorUtils::RemoveVariable(Struct, Guid))
            {
                return true;
            }
        }
    }
    FFrame::KismetExecutionMessage(*FString::Printf(TEXT("DeleteStructField %s: requires an existing field in a UserDefinedStruct with at least two fields; RemoveVariable must succeed"), *Name), ELogVerbosity::Error);
    return false;
}

bool UUnrealBPBridgeLibrary::MoveStructField(UUserDefinedStruct* Struct, const FString& Name, const FString& RelativeTo, bool bAfter)
{
    if (Struct && Name != RelativeTo)
    {
        const auto& Fields = FStructureEditorUtils::GetVarDesc(Struct);
        const int32 Index = Fields.IndexOfByPredicate(
            [&Name](const FStructVariableDescription& Item) { return Item.FriendlyName == Name; });
        const int32 RelativeIndex = Fields.IndexOfByPredicate(
            [&RelativeTo](const FStructVariableDescription& Item) { return Item.FriendlyName == RelativeTo; });
        if (Index != INDEX_NONE && RelativeIndex != INDEX_NONE)
        {
            if (Index == RelativeIndex + (bAfter ? 1 : -1))
            {
                return true;
            }
            const FGuid Guid = Fields[Index].VarGuid;
            const FGuid RelativeGuid = Fields[RelativeIndex].VarGuid;
            if (FStructureEditorUtils::MoveVariable(Struct, Guid, RelativeGuid,
                bAfter ? FStructureEditorUtils::PositionBelow : FStructureEditorUtils::PositionAbove))
            {
                return true;
            }
        }
    }
    FFrame::KismetExecutionMessage(*FString::Printf(TEXT("MoveStructField %s: requires two distinct existing fields in a UserDefinedStruct; MoveVariable must succeed"), *Name), ELogVerbosity::Error);
    return false;
}

bool UUnrealBPBridgeLibrary::SetStructFieldTooltip(UUserDefinedStruct* Struct, const FString& Name, const FString& Tooltip)
{
    if (Struct)
    {
        const FStructVariableDescription* Field = FStructureEditorUtils::GetVarDesc(Struct).FindByPredicate(
            [&Name](const FStructVariableDescription& Item) { return Item.FriendlyName == Name; });
        if (Field)
        {
            const FGuid Guid = Field->VarGuid;
            if (FStructureEditorUtils::GetVariableTooltip(Struct, Guid) == Tooltip
                || FStructureEditorUtils::ChangeVariableTooltip(Struct, Guid, Tooltip))
            {
                return true;
            }
        }
    }
    FFrame::KismetExecutionMessage(*FString::Printf(TEXT("SetStructFieldTooltip %s: requires an existing field in a UserDefinedStruct; ChangeVariableTooltip must succeed"), *Name), ELogVerbosity::Error);
    return false;
}

bool UUnrealBPBridgeLibrary::IsDataAssetClassAllowed(UClass* AssetClass)
{
    return AssetClass && AssetClass->IsChildOf(UDataAsset::StaticClass())
        && !AssetClass->HasAnyClassFlags(CLASS_Abstract | CLASS_Deprecated | CLASS_NewerVersionExists | CLASS_HideDropDown);
}

bool UUnrealBPBridgeLibrary::ConfigureAnimCompositeFactory(UAnimCompositeFactory* Factory, USkeleton* Skeleton)
{
    if (!Factory || !Skeleton)
    {
        FFrame::KismetExecutionMessage(TEXT("ConfigureAnimCompositeFactory requires a factory and skeleton"), ELogVerbosity::Error);
        return false;
    }
    Factory->TargetSkeleton = Skeleton;
    return true;
}

bool UUnrealBPBridgeLibrary::ConfigurePreviewMeshCollectionFactory(UPreviewMeshCollectionFactory* Factory, USkeleton* Skeleton)
{
    if (!Factory || !Skeleton)
    {
        FFrame::KismetExecutionMessage(TEXT("ConfigurePreviewMeshCollectionFactory requires a factory and skeleton"), ELogVerbosity::Error);
        return false;
    }
    Factory->CurrentSkeleton = Skeleton;
    return true;
}

bool UUnrealBPBridgeLibrary::ConfigurePCGGraphInstanceFactory(UFactory* Factory, UObject* ParentGraph)
{
    // PCGGraphInstanceFactory is private to PCGEditor; configure its reflected field without a private header dependency.
    if (!Factory || Factory->GetClass()->GetPathName() != TEXT("/Script/PCGEditor.PCGGraphInstanceFactory"))
    {
        FFrame::KismetExecutionMessage(TEXT("ConfigurePCGGraphInstanceFactory requires PCGGraphInstanceFactory"), ELogVerbosity::Error);
        return false;
    }
    FObjectPropertyBase* Property = FindFProperty<FObjectPropertyBase>(Factory->GetClass(), TEXT("ParentGraph"));
    if (!Property || Property->PropertyClass->GetPathName() != TEXT("/Script/PCG.PCGGraphInterface"))
    {
        FFrame::KismetExecutionMessage(TEXT("PCGGraphInstanceFactory.ParentGraph schema does not match PCGGraphInterface"), ELogVerbosity::Error);
        return false;
    }
    if (!ParentGraph || !ParentGraph->IsA(Property->PropertyClass))
    {
        FFrame::KismetExecutionMessage(TEXT("ConfigurePCGGraphInstanceFactory requires a PCGGraphInterface parent"), ELogVerbosity::Error);
        return false;
    }
    Property->SetObjectPropertyValue_InContainer(Factory, ParentGraph);
    return true;
}

bool UUnrealBPBridgeLibrary::IsSoundEffectPresetClassAllowed(UClass* AssetClass)
{
    return AssetClass
        && (AssetClass->IsChildOf(USoundEffectSourcePreset::StaticClass()) || AssetClass->IsChildOf(USoundEffectSubmixPreset::StaticClass()))
        && !AssetClass->HasAnyClassFlags(CLASS_Abstract | CLASS_Deprecated | CLASS_NewerVersionExists);
}

bool UUnrealBPBridgeLibrary::ConfigureStateTreeFactory(UStateTreeFactory* Factory, UClass* SchemaClass)
{
    if (!Factory || !SchemaClass || !SchemaClass->IsChildOf(UStateTreeSchema::StaticClass())
        || SchemaClass->HasAnyClassFlags(CLASS_Abstract | CLASS_Deprecated | CLASS_NewerVersionExists | CLASS_HideDropDown))
    {
        FFrame::KismetExecutionMessage(TEXT("ConfigureStateTreeFactory requires a factory and a selectable StateTreeSchema class"), ELogVerbosity::Error);
        return false;
    }
    Factory->SetSchemaClass(SchemaClass);
    return true;
}

bool UUnrealBPBridgeLibrary::IsConcreteFactoryClass(UClass* AssetClass)
{
    return AssetClass && !AssetClass->HasAnyClassFlags(CLASS_Abstract | CLASS_Deprecated | CLASS_NewerVersionExists);
}

bool UUnrealBPBridgeLibrary::IsEditorUtilityParentAllowed(UClass* ParentClass)
{
    return ParentClass && IsEditorOnlyObject(ParentClass)
        && !ParentClass->IsChildOf(UEditorUtilityWidget::StaticClass())
        && (ParentClass->GetPathName() == TEXT("/Script/Blutility.EditorFunctionLibrary") || FKismetEditorUtilities::CanCreateBlueprintOfClass(ParentClass));
}

bool UUnrealBPBridgeLibrary::HasCameraDirectorClass(UCameraAsset* Asset, UClass* DirectorClass)
{
    return Asset && DirectorClass && Asset->GetCameraDirector() && Asset->GetCameraDirector()->GetClass() == DirectorClass;
}

namespace
{
FString MaterialJson(const TSharedRef<FJsonObject>& Object)
{
    FString Result;
    FJsonSerializer::Serialize(Object, TJsonWriterFactory<>::Create(&Result));
    return Result;
}
FString MaterialError(const FString& Message)
{
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    Result->SetStringField(TEXT("error"), Message);
    return MaterialJson(Result);
}
bool MaterialProperty(const FString& Name, EMaterialProperty& Property)
{
    const UEnum* Enum = StaticEnum<EMaterialProperty>();
    const int64 Value = Enum->GetValueByNameString(Name);
    if (Value == INDEX_NONE || Value < 0 || Value >= MP_MAX || Name.EndsWith(TEXT("_DEPRECATED")))
    {
        FFrame::KismetExecutionMessage(*FString::Printf(TEXT("Unknown material property: %s"), *Name), ELogVerbosity::Error);
        return false;
    }
    Property = static_cast<EMaterialProperty>(Value);
    return true;
}
TSharedRef<FJsonObject> MaterialReference(const UObject* Object)
{
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    Result->SetStringField(TEXT("refPath"), Object->GetPathName());
    return Result;
}
}

FString UUnrealBPBridgeLibrary::GetMaterialOutputs(UMaterial* Material, const TArray<FString>& Properties)
{
    if (!Material) return MaterialError(TEXT("Expected Material"));
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    for (const FString& Name : Properties)
    {
        EMaterialProperty Property;
        if (!MaterialProperty(Name, Property)) return MaterialError(TEXT("Unknown material property: ") + Name);
        TSharedRef<FJsonObject> Entry = MakeShared<FJsonObject>();
        if (!Material->GetExpressionInputForProperty(Property))
        {
            Entry->SetBoolField(TEXT("unavailable"), true);
            Entry->SetStringField(TEXT("reason"), TEXT("No expression input exists for this property in this engine"));
        }
        else
        {
            UMaterialExpression* Expression = UMaterialEditingLibrary::GetMaterialPropertyInputNode(Material, Property);
            Entry->SetStringField(TEXT("input_name"), TEXT(""));
            if (Expression) Entry->SetObjectField(TEXT("expression"), MaterialReference(Expression));
            else Entry->SetStringField(TEXT("expression"), TEXT("None"));
            Entry->SetStringField(TEXT("output_name"), UMaterialEditingLibrary::GetMaterialPropertyInputNodeOutputName(Material, Property));
        }
        Result->SetObjectField(Name, Entry);
    }
    return MaterialJson(Result);
}

bool UUnrealBPBridgeLibrary::ConnectMaterialOutput(UMaterial* Material, const FString& Name, UMaterialExpression* Expression, const FString& Output)
{
    EMaterialProperty Property;
    if (!Material || !Expression || Expression->GetOuter() != Material || !MaterialProperty(Name, Property))
    {
        FFrame::KismetExecutionMessage(TEXT("ConnectMaterialOutput requires an owned expression and valid property"), ELogVerbosity::Error);
        return false;
    }
    return UMaterialEditingLibrary::ConnectMaterialProperty(Expression, Output, Property);
}

bool UUnrealBPBridgeLibrary::DisconnectMaterialOutput(UMaterial* Material, const FString& Name)
{
    EMaterialProperty Property;
    if (!Material || !MaterialProperty(Name, Property))
    {
        FFrame::KismetExecutionMessage(TEXT("DisconnectMaterialOutput requires a material and valid property"), ELogVerbosity::Error);
        return false;
    }
    return UMaterialEditingLibrary::DisconnectMaterialProperty(Material, Property);
}

FString UUnrealBPBridgeLibrary::GetMaterialDiagnostics(UMaterial* Material)
{
    if (!Material) return MaterialError(TEXT("Expected Material"));
    FMaterialResource* Resource = Material->GetMaterialResource(GMaxRHIShaderPlatform);
    if (!Resource) return MaterialError(TEXT("No material resource for the active editor shader platform"));
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    Result->SetObjectField(TEXT("asset"), MaterialReference(Material));
    Result->SetNumberField(TEXT("shader_platform"), static_cast<int32>(GMaxRHIShaderPlatform));
    Result->SetBoolField(TEXT("finished"), Resource->IsCompilationFinished());
    TArray<TSharedPtr<FJsonValue>> Errors;
    for (const FString& Error : Resource->GetCompileErrors()) Errors.Add(MakeShared<FJsonValueString>(Error));
    Result->SetArrayField(TEXT("errors"), Errors);
    TArray<TSharedPtr<FJsonValue>> Expressions;
    for (const UMaterialExpression* Expression : Resource->GetErrorExpressions())
    {
        if (Expression) Expressions.Add(MakeShared<FJsonValueObject>(MaterialReference(Expression)));
    }
    Result->SetArrayField(TEXT("error_expressions"), Expressions);
    return MaterialJson(Result);
}

FString UUnrealBPBridgeLibrary::GetMaterialParameters(UMaterialInterface* Material)
{
    if (!Material) return MaterialError(TEXT("Expected MaterialInterface"));
    TArray<TSharedPtr<FJsonValue>> Result;
    const EMaterialParameterType Types[] = {EMaterialParameterType::Scalar, EMaterialParameterType::Vector, EMaterialParameterType::Texture, EMaterialParameterType::StaticSwitch};
    const TCHAR* Names[] = {TEXT("Scalar"), TEXT("Vector"), TEXT("Texture"), TEXT("StaticSwitch")};
    for (int32 TypeIndex = 0; TypeIndex < 4; ++TypeIndex)
    {
        TArray<FMaterialParameterInfo> Infos;
        TArray<FGuid> Ids;
        Material->GetAllParameterInfoOfType(Types[TypeIndex], Infos, Ids);
        for (const FMaterialParameterInfo& Info : Infos)
        {
            TSharedRef<FJsonObject> Entry = MakeShared<FJsonObject>();
            Entry->SetStringField(TEXT("name"), Info.Name.ToString());
            Entry->SetStringField(TEXT("type"), Names[TypeIndex]);
            Entry->SetStringField(TEXT("association"), StaticEnum<EMaterialParameterAssociation>()->GetNameStringByValue(Info.Association));
            Entry->SetNumberField(TEXT("index"), Info.Index);
            Result.Add(MakeShared<FJsonValueObject>(Entry));
        }
    }
    FString Json;
    FJsonSerializer::Serialize(Result, TJsonWriterFactory<>::Create(&Json));
    return Json;
}

FString UUnrealBPBridgeLibrary::EditMaterialParameter(UMaterialInstanceConstant* Instance, const FString& Action, const FString& Arguments)
{
    if (!Instance) return MaterialError(TEXT("Expected MaterialInstanceConstant"));
    TSharedPtr<FJsonObject> Args;
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Arguments), Args) || !Args.IsValid())
        return MaterialError(TEXT("Invalid parameter arguments JSON"));
    FString Selector;
    if (!Args->TryGetStringField(TEXT("name"), Selector)) return MaterialError(TEXT("Parameter name or identity JSON is required"));
    FString Name = Selector;
    int64 Association = GlobalParameter;
    int32 Index = INDEX_NONE;
    const bool ExplicitIdentity = Selector.StartsWith(TEXT("{"));
    if (ExplicitIdentity)
    {
        TSharedPtr<FJsonObject> Identity;
        FString AssociationName;
        double IndexNumber;
        if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Selector), Identity) || !Identity.IsValid() ||
            !Identity->TryGetStringField(TEXT("name"), Name) || !Identity->TryGetStringField(TEXT("association"), AssociationName) ||
            !Identity->TryGetNumberField(TEXT("index"), IndexNumber))
            return MaterialError(TEXT("Identity requires name, association and index"));
        Association = StaticEnum<EMaterialParameterAssociation>()->GetValueByNameString(AssociationName);
        if (Association < LayerParameter || Association > GlobalParameter || IndexNumber != FMath::FloorToDouble(IndexNumber) || IndexNumber < -1 || IndexNumber > MAX_int32)
            return MaterialError(TEXT("Invalid parameter association/index"));
        Index = static_cast<int32>(IndexNumber);
    }
    const EMaterialParameterType Types[] = {EMaterialParameterType::Scalar, EMaterialParameterType::Vector, EMaterialParameterType::Texture, EMaterialParameterType::StaticSwitch};
    FMaterialParameterInfo Selected;
    EMaterialParameterType Type = EMaterialParameterType::None;
    int32 Matches = 0;
    for (EMaterialParameterType Candidate : Types)
    {
        TArray<FMaterialParameterInfo> Infos;
        TArray<FGuid> Ids;
        Instance->GetAllParameterInfoOfType(Candidate, Infos, Ids);
        for (const FMaterialParameterInfo& Info : Infos)
        {
            if (Info.Name.ToString() == Name && (!ExplicitIdentity || (Info.Association == Association && Info.Index == Index)))
            {
                Selected = Info;
                Type = Candidate;
                ++Matches;
            }
        }
    }
    if (Matches != 1) return MaterialError(TEXT("Expected exactly one parameter; use an identity from list material_parameters"));
    FMaterialParameterMetadata Meta;
    if (!Instance->GetParameterValue(Type, Selected, Meta)) return MaterialError(TEXT("Cannot read selected parameter"));
    const bool Set = Action == TEXT("material_parameter_set");
    const bool Override = Action == TEXT("material_override");
    if (!Set && !Override && Action != TEXT("material_parameter_get")) return MaterialError(TEXT("Unknown parameter action"));
    bool Enable = false;
    if (Override && !Args->TryGetBoolField(TEXT("value"), Enable)) return MaterialError(TEXT("Override requires boolean value"));
    float Scalar = Meta.Value.Type == EMaterialParameterType::Scalar ? Meta.Value.AsScalar() : 0;
    FLinearColor Vector = Type == EMaterialParameterType::Vector ? Meta.Value.AsLinearColor() : FLinearColor::Black;
    UTexture* Texture = Type == EMaterialParameterType::Texture ? Meta.Value.Texture : nullptr;
    bool Switch = Type == EMaterialParameterType::StaticSwitch ? Meta.Value.AsStaticSwitch() : false;
    if (Set)
    {
        double Number;
        FString TexturePath;
        const TSharedPtr<FJsonObject>* Color;
        if (Type == EMaterialParameterType::Scalar)
        {
            if (!Args->TryGetNumberField(TEXT("value"), Number)) return MaterialError(TEXT("Scalar requires a number"));
            Scalar = Number;
        }
        else if (Type == EMaterialParameterType::Vector)
        {
            double R, G, B, A;
            if (!Args->TryGetObjectField(TEXT("value"), Color) || !(*Color)->TryGetNumberField(TEXT("r"), R) ||
                !(*Color)->TryGetNumberField(TEXT("g"), G) || !(*Color)->TryGetNumberField(TEXT("b"), B) || !(*Color)->TryGetNumberField(TEXT("a"), A))
                return MaterialError(TEXT("Vector requires numeric r,g,b,a"));
            Vector = FLinearColor(R, G, B, A);
        }
        else if (Type == EMaterialParameterType::Texture)
        {
            if (!Args->TryGetStringField(TEXT("value"), TexturePath)) return MaterialError(TEXT("Texture requires an asset path"));
            Texture = LoadObject<UTexture>(nullptr, *TexturePath);
            if (!Texture) return MaterialError(TEXT("Texture asset could not be loaded"));
        }
        else if (!Args->TryGetBoolField(TEXT("value"), Switch)) return MaterialError(TEXT("StaticSwitch requires a boolean"));
    }
    if (Set || (Override && Enable))
    {
        Instance->Modify();
        if (Type == EMaterialParameterType::Scalar) Instance->SetScalarParameterValueEditorOnly(Selected, Scalar);
        else if (Type == EMaterialParameterType::Vector) Instance->SetVectorParameterValueEditorOnly(Selected, Vector);
        else if (Type == EMaterialParameterType::Texture) Instance->SetTextureParameterValueEditorOnly(Selected, Texture);
        else Instance->SetStaticSwitchParameterValueEditorOnly(Selected, Switch);
    }
    else if (Override && !Enable && Meta.bOverride)
    {
        Instance->Modify();
        auto Remove = [&Selected](auto& Values) { return Values.RemoveAll([&Selected](const auto& Value) { return Value.ParameterInfo == Selected; }); };
        bool Removed = false;
        if (Type == EMaterialParameterType::Scalar) Removed = Remove(Instance->ScalarParameterValues) > 0;
        else if (Type == EMaterialParameterType::Vector) Removed = Remove(Instance->VectorParameterValues) > 0;
        else if (Type == EMaterialParameterType::Texture) Removed = Remove(Instance->TextureParameterValues) > 0;
        else
        {
            FStaticParameterSet Parameters = Instance->GetStaticParameters();
            for (auto& Value : Parameters.StaticSwitchParameters)
                if (Value.ParameterInfo == Selected) { Value.bOverride = false; Removed = true; }
            if (Removed) Instance->UpdateStaticPermutation(Parameters);
        }
        if (!Removed) return MaterialError(TEXT("Override metadata has no matching local parameter"));
    }
    if (Set || Override)
    {
        UMaterialEditingLibrary::UpdateMaterialInstance(Instance);
        if (Type == EMaterialParameterType::StaticSwitch)
        {
            const TArray<FString> Errors = UMaterialEditingLibrary::RecompileMaterial(Instance->GetMaterial());
            if (!Errors.IsEmpty()) return MaterialError(FString::Join(Errors, TEXT("\n")));
        }
        UMaterialEditingLibrary::RefreshMaterialInstanceEditor(Instance);
        if (!Instance->GetParameterValue(Type, Selected, Meta)) return MaterialError(TEXT("Parameter readback failed"));
    }
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    Result->SetStringField(TEXT("name"), Selected.Name.ToString());
    Result->SetStringField(TEXT("association"), StaticEnum<EMaterialParameterAssociation>()->GetNameStringByValue(Selected.Association));
    Result->SetNumberField(TEXT("index"), Selected.Index);
    Result->SetBoolField(TEXT("override"), Meta.bOverride);
    if (Type == EMaterialParameterType::Scalar) Result->SetNumberField(TEXT("value"), Meta.Value.AsScalar());
    else if (Type == EMaterialParameterType::Vector)
    {
        FLinearColor Value = Meta.Value.AsLinearColor();
        TSharedRef<FJsonObject> Color = MakeShared<FJsonObject>();
        Color->SetNumberField(TEXT("r"), Value.R); Color->SetNumberField(TEXT("g"), Value.G);
        Color->SetNumberField(TEXT("b"), Value.B); Color->SetNumberField(TEXT("a"), Value.A);
        Result->SetObjectField(TEXT("value"), Color);
    }
    else if (Type == EMaterialParameterType::Texture)
    {
        if (Meta.Value.Texture) Result->SetObjectField(TEXT("value"), MaterialReference(Meta.Value.Texture));
        else Result->SetField(TEXT("value"), MakeShared<FJsonValueNull>());
    }
    else Result->SetBoolField(TEXT("value"), Meta.Value.AsStaticSwitch());
    return MaterialJson(Result);
}

bool UUnrealBPBridgeLibrary::SetMaterialLayerStack(UMaterialExpressionMaterialAttributeLayers* Expression, const FString& Json)
{
    auto Fail = [](const FString& Message)
    {
        FFrame::KismetExecutionMessage(*(TEXT("SetMaterialLayerStack: ") + Message), ELogVerbosity::Error);
        return false;
    };
    if (!Expression) return Fail(TEXT("Expected MaterialAttributeLayers expression"));
    TSharedPtr<FJsonObject> Object;
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json), Object) || !Object.IsValid())
        return Fail(TEXT("Invalid stack JSON"));
    TArray<UMaterialFunctionInterface*> Layers;
    TArray<UMaterialFunctionInterface*> Blends;
    auto ReadFunctions = [&Object](const TCHAR* Field, TArray<UMaterialFunctionInterface*>& Out, EMaterialFunctionUsage Usage)
    {
        const TArray<TSharedPtr<FJsonValue>>* Entries;
        if (!Object->TryGetArrayField(Field, Entries)) return false;
        for (const TSharedPtr<FJsonValue>& Entry : *Entries)
        {
            const TSharedPtr<FJsonObject>* Ref;
            FString Path;
            if (!Entry->TryGetObject(Ref) || !(*Ref)->TryGetStringField(TEXT("refPath"), Path)) return false;
            UMaterialFunctionInterface* Function = LoadObject<UMaterialFunctionInterface>(nullptr, *Path);
            if (!Function || Function->GetMaterialFunctionUsage() != Usage) return false;
            Out.Add(Function);
        }
        return true;
    };
    if (!ReadFunctions(TEXT("layers"), Layers, EMaterialFunctionUsage::MaterialLayer) ||
        !ReadFunctions(TEXT("blends"), Blends, EMaterialFunctionUsage::MaterialLayerBlend))
        return Fail(TEXT("Layer/blend references must resolve to functions of the matching usage"));
    const TSharedPtr<FJsonObject>* EditorJson;
    if (!Object->TryGetObjectField(TEXT("editorOnly"), EditorJson)) return Fail(TEXT("editorOnly metadata is required"));
    FMaterialLayersFunctions Value;
    FText ImportError;
    if (!FJsonObjectConverter::JsonObjectToUStruct((*EditorJson).ToSharedRef(), FMaterialLayersFunctionsEditorOnlyData::StaticStruct(), &Value.EditorOnly, 0, 0, true, &ImportError))
        return Fail(ImportError.ToString());
    Value.Layers = Layers;
    Value.Blends = Blends;
    const int32 Count = Layers.Num();
    const FMaterialLayersFunctionsEditorOnlyData& Editor = Value.EditorOnly;
    if (Count < 1 || Blends.Num() != Count - 1 || Editor.LayerStates.Num() != Count || Editor.LayerNames.Num() != Count ||
        Editor.RestrictToLayerRelatives.Num() != Count || Editor.RestrictToBlendRelatives.Num() != Count - 1 ||
        Editor.LayerGuids.Num() != Count || Editor.LayerLinkStates.Num() != Count)
        return Fail(TEXT("Layer, blend and metadata array lengths are inconsistent"));
    TSet<FGuid> Guids;
    for (const FGuid& Guid : Editor.LayerGuids)
    {
        if (!Guid.IsValid() || Guids.Contains(Guid)) return Fail(TEXT("Layer GUIDs must be valid and unique"));
        Guids.Add(Guid);
    }
    for (EMaterialLayerLinkState State : Editor.LayerLinkStates)
        if (State == EMaterialLayerLinkState::Uninitialized) return Fail(TEXT("Layer link state must be initialized"));
    Expression->Modify();
    Expression->DefaultLayers = MoveTemp(Value);
    FProperty* Property = FindFProperty<FProperty>(UMaterialExpressionMaterialAttributeLayers::StaticClass(), GET_MEMBER_NAME_CHECKED(UMaterialExpressionMaterialAttributeLayers, DefaultLayers));
    check(Property);
    FPropertyChangedEvent Event(Property);
    Expression->PostEditChangeProperty(Event);
    return true;
}
