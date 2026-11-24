# Factory inventory

Snapshot: 2026-09-12; engine 5.8.2-56702186+++UE5+Release-5.8; SpaceGovernor.

268 discovered factories; 209 declare create_new and a supported class, 59 do not satisfy both defaults. These are discovery candidates, not a promise that ConfigureProperties can be skipped.

Status is intentionally explicit: unreviewed is not unsupported forever. Non-default factories may be import-only or need configuration before creation.

| Factory | Asset class | Status |
| --- | --- | --- |
| `/Script/UnrealEd.Factory` | `None` | Defaults insufficient; inspect import/configuration path |
| `/Script/AnimGraph.AnimSequenceTransformProviderLayerStackFactory` | `/Script/Engine.AnimSequenceTransformProviderLayerStack` | Rule configured; creation verified |
| `/Script/AnimGraph.AnimSequenceTransformProviderSequenceListFactory` | `/Script/Engine.AnimSequenceTransformProviderSequenceList` | Rule configured; creation verified |
| `/Script/AnimGraph.AnimSequenceTransformProviderBlendSpaceListFactory` | `/Script/Engine.AnimSequenceTransformProviderBlendSpaceList` | Rule configured; creation verified |
| `/Script/DataLayerEditor.DataLayerFactory` | `/Script/Engine.DataLayerAsset` | Rule configured |
| `/Script/DataLayerEditor.ExternalDataLayerFactory` | `/Script/Engine.ExternalDataLayerAsset` | Requires external data layer editor setting review |
| `/Script/Blutility.EditorUtilityBlueprintFactory` | `/Script/Blutility.EditorUtilityBlueprint` | Creation/save and native postconditions or parent validation verified |
| `/Script/Blutility.EditorUtilityWidgetBlueprintFactory` | `/Script/Blutility.EditorUtilityWidgetBlueprint` | Rule configured; creation verified |
| `/Script/VirtualTexturingEditor.MaterialCacheVirtualTextureTagFactory` | `/Script/Engine.MaterialCacheVirtualTextureTag` | Rule configured |
| `/Script/VirtualTexturingEditor.RuntimeVirtualTextureFactory` | `/Script/Engine.RuntimeVirtualTexture` | Rule configured |
| `/Script/VirtualTexturingEditor.VirtualTextureBuilderFactory` | `/Script/Engine.VirtualTextureBuilder` | Rule configured |
| `/Script/UMGEditor.SlateVectorArtDataFactory` | `/Script/UMG.SlateVectorArtData` | Rule configured |
| `/Script/UMGEditor.WidgetBlueprintFactory` | `/Script/UMGEditor.WidgetBlueprint` | Rule configured; creation verified |
| `/Script/AudioEditor.AudioBusFactory` | `/Script/Engine.AudioBus` | Rule configured |
| `/Script/AudioEditor.DialogueVoiceFactory` | `/Script/Engine.DialogueVoice` | Rule configured |
| `/Script/AudioEditor.DialogueWaveFactory` | `/Script/Engine.DialogueWave` | Rule configured; default creation verified |
| `/Script/AudioEditor.SoundFactory` | `/Script/Engine.SoundWave` | Defaults insufficient; inspect import/configuration path |
| `/Script/AudioEditor.ReimportSoundFactory` | `/Script/Engine.SoundWave` | Defaults insufficient; inspect import/configuration path |
| `/Script/AudioEditor.ReverbEffectFactory` | `/Script/Engine.ReverbEffect` | Rule configured |
| `/Script/AudioEditor.SoundAttenuationFactory` | `/Script/Engine.SoundAttenuation` | Rule configured |
| `/Script/AudioEditor.SoundClassFactory` | `/Script/Engine.SoundClass` | Rule configured |
| `/Script/AudioEditor.SoundConcurrencyFactory` | `/Script/Engine.SoundConcurrency` | Rule configured |
| `/Script/AudioEditor.SoundCueFactoryNew` | `/Script/Engine.SoundCue` | Rule configured; default creation verified |
| `/Script/AudioEditor.SoundMixFactory` | `/Script/Engine.SoundMix` | Rule configured |
| `/Script/AudioEditor.SoundSourceBusFactory` | `/Script/Engine.SoundSourceBus` | Rule configured |
| `/Script/AudioEditor.SoundSourceEffectFactory` | `/Script/Engine.SoundEffectSourcePreset` | Protocol 5 creation/save/class and abstract rejection verified |
| `/Script/AudioEditor.SoundSourceEffectChainFactory` | `/Script/Engine.SoundEffectSourcePresetChain` | Rule configured; default creation verified |
| `/Script/AudioEditor.SoundSubmixEffectFactory` | `/Script/Engine.SoundEffectSubmixPreset` | Protocol 5 creation/save/class and abstract rejection verified |
| `/Script/AudioEditor.SoundSubmixFactory` | `/Script/Engine.SoundSubmix` | Rule configured; default creation verified |
| `/Script/AudioEditor.SoundfieldSubmixFactory` | `/Script/Engine.SoundfieldSubmix` | Rule configured; default creation verified |
| `/Script/AudioEditor.EndpointSubmixFactory` | `/Script/Engine.EndpointSubmix` | Rule configured; default creation verified |
| `/Script/AudioEditor.SoundfieldEndpointSubmixFactory` | `/Script/Engine.SoundfieldEndpointSubmix` | Rule configured; default creation verified |
| `/Script/FoliageEdit.FoliageType_InstancedStaticMeshFactory` | `/Script/Foliage.FoliageType_InstancedStaticMesh` | Rule configured; default creation verified |
| `/Script/FoliageEdit.FoliageType_ActorFactory` | `/Script/Foliage.FoliageType_Actor` | Rule configured; default creation verified |
| `/Script/FoliageEdit.LandscapeGrassTypeFactory` | `/Script/Landscape.LandscapeGrassType` | Rule configured |
| `/Script/FoliageEdit.ProceduralFoliageSpawnerFactory` | `/Script/Foliage.ProceduralFoliageSpawner` | Conditional rule; disabled setting rejection verified; user chose to keep disabled |
| `/Script/UnrealEd.BlendSpaceFactory1D` | `/Script/Engine.BlendSpace1D` | Rule configured |
| `/Script/UnrealEd.AimOffsetBlendSpaceFactory1D` | `/Script/Engine.AimOffsetBlendSpace1D` | Rule configured |
| `/Script/UnrealEd.BlendSpaceFactoryNew` | `/Script/Engine.BlendSpace` | Rule configured |
| `/Script/UnrealEd.AimOffsetBlendSpaceFactoryNew` | `/Script/Engine.AimOffsetBlendSpace` | Rule configured |
| `/Script/UnrealEd.BlueprintFactory` | `/Script/Engine.Blueprint` | Rule configured |
| `/Script/UnrealEd.BlueprintFunctionLibraryFactory` | `/Script/Engine.Blueprint` | Rule configured |
| `/Script/UnrealEd.BlueprintInterfaceFactory` | `/Script/Engine.Blueprint` | Rule configured |
| `/Script/UnrealEd.BlueprintMacroFactory` | `/Script/Engine.Blueprint` | Rule configured |
| `/Script/ModelContextProtocolEditor.ModelContextProtocolToolLibraryFactory` | `/Script/ModelContextProtocolEngine.ModelContextProtocolToolLibraryBlueprint` | Rule configured; default creation verified |
| `/Script/ModelContextProtocolEditor.ModelContextProtocolEditorToolLibraryFactory` | `/Script/ModelContextProtocolEditor.ModelContextProtocolEditorToolLibraryBlueprint` | Rule configured; default creation verified |
| `/Script/UnrealEd.CanvasRenderTarget2DFactoryNew` | `/Script/Engine.CanvasRenderTarget2D` | Rule configured; creation verified |
| `/Script/UnrealEd.CurveFactory` | `/Script/Engine.CurveBase` | Creation/save and selected class verified |
| `/Script/UnrealEd.CurveFloatFactory` | `/Script/Engine.CurveFloat` | Rule configured |
| `/Script/UnrealEd.CurveLinearColorFactory` | `/Script/Engine.CurveLinearColor` | Rule configured |
| `/Script/UnrealEd.CurveVectorFactory` | `/Script/Engine.CurveVector` | Rule configured |
| `/Script/UnrealEd.CurveImportFactory` | `/Script/Engine.CurveBase` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.CurveLinearColorAtlasFactory` | `/Script/Engine.CurveLinearColorAtlas` | Rule configured; creation verified |
| `/Script/UnrealEd.DataAssetFactory` | `/Script/Engine.DataAsset` | Rule configured; creation verified |
| `/Script/UnrealEd.EnumFactory` | `/Script/Engine.UserDefinedEnum` | Rule configured |
| `/Script/UnrealEd.FontFactory` | `/Script/Engine.Font` | Default creation/save verified; see current verification notes |
| `/Script/UnrealEd.FontFileImportFactory` | `/Script/Engine.FontFace` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ForceFeedbackAttenuationFactory` | `/Script/Engine.ForceFeedbackAttenuation` | Rule configured |
| `/Script/UnrealEd.ForceFeedbackEffectFactory` | `/Script/Engine.ForceFeedbackEffect` | Rule configured |
| `/Script/UnrealEd.HapticFeedbackEffectBufferFactory` | `/Script/Engine.HapticFeedbackEffect_Buffer` | Rule configured |
| `/Script/UnrealEd.HapticFeedbackEffectCurveFactory` | `/Script/Engine.HapticFeedbackEffect_Curve` | Rule configured |
| `/Script/UnrealEd.HapticFeedbackEffectSoundWaveFactory` | `/Script/Engine.HapticFeedbackEffect_SoundWave` | Rule configured |
| `/Script/UnrealEd.LevelFactory` | `/Script/Engine.World` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.MaterialFactoryNew` | `/Script/Engine.Material` | Rule configured |
| `/Script/UnrealEd.MaterialFunctionFactoryNew` | `/Script/Engine.MaterialFunction` | Rule configured |
| `/Script/UnrealEd.MaterialFunctionInstanceFactory` | `/Script/Engine.MaterialFunctionInstance` | Rule configured; creation verified |
| `/Script/UnrealEd.MaterialFunctionMaterialLayerInstanceFactory` | `/Script/Engine.MaterialFunctionMaterialLayerInstance` | Rule configured; creation verified |
| `/Script/UnrealEd.MaterialFunctionMaterialLayerBlendInstanceFactory` | `/Script/Engine.MaterialFunctionMaterialLayerBlendInstance` | Rule configured; creation verified |
| `/Script/UnrealEd.MaterialFunctionMaterialLayerBlendFactory` | `/Script/Engine.MaterialFunctionMaterialLayerBlend` | Rule configured |
| `/Script/UnrealEd.MaterialFunctionMaterialLayerFactory` | `/Script/Engine.MaterialFunctionMaterialLayer` | Rule configured |
| `/Script/UnrealEd.MaterialInstanceConstantFactoryNew` | `/Script/Engine.MaterialInstanceConstant` | Rule configured |
| `/Script/UnrealEd.SparseVolumeTextureMaterialInstanceFactoryNew` | `/Script/Engine.MaterialInstanceConstant` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.MaterialParameterCollectionFactoryNew` | `/Script/Engine.MaterialParameterCollection` | Rule configured |
| `/Script/UnrealEd.ModelFactory` | `/Script/Engine.Model` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.NeuralProfileFactory` | `/Script/Engine.NeuralProfile` | Rule configured |
| `/Script/UnrealEd.ObjectLibraryFactory` | `/Script/Engine.ObjectLibrary` | Rule configured |
| `/Script/UnrealEd.PackageFactory` | `/Script/CoreUObject.Package` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ParticleSystemFactoryNew` | `/Script/Engine.ParticleSystem` | Rule configured; default creation verified |
| `/Script/UnrealEd.PhysicalMaterialFactoryNew` | `/Script/PhysicsCore.PhysicalMaterial` | Rule configured; creation verified |
| `/Script/UnrealEd.PhysicalMaterialMaskFactory` | `/Script/Engine.PhysicalMaterialMask` | Rule configured; creation verified |
| `/Script/UnrealEd.PolysFactory` | `/Script/Engine.Polys` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.PreviewMeshCollectionFactory` | `/Script/Engine.PreviewMeshCollection` | Rule configured; creation verified |
| `/Script/UnrealEd.CSVImportFactory` | `/Script/Engine.DataTable` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ReimportCurveFactory` | `/Script/Engine.CurveBase` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ReimportCurveTableFactory` | `/Script/Engine.DataTable` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ReimportDataTableFactory` | `/Script/Engine.DataTable` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.FbxFactory` | `None` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ReimportFbxAnimSequenceFactory` | `/Script/Engine.AnimSequence` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ReimportFbxSkeletalMeshFactory` | `/Script/Engine.SkeletalMesh` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ReimportFbxStaticMeshFactory` | `/Script/Engine.StaticMesh` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.TextureFactory` | `/Script/Engine.Texture` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ReimportTextureFactory` | `/Script/Engine.Texture` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.TrueTypeFontFactory` | `/Script/Engine.Font` | Needs review |
| `/Script/UnrealEd.VectorFieldStaticFactory` | `/Script/Engine.VectorFieldStatic` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ReimportVectorFieldStaticFactory` | `/Script/Engine.VectorFieldStatic` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.SceneImportFactory` | `None` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.FbxSceneImportFactory` | `/Script/Engine.World` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.ReimportFbxSceneFactory` | `/Script/UnrealEd.FbxSceneImportData` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.SpecularProfileFactory` | `/Script/Engine.SpecularProfile` | Rule configured |
| `/Script/UnrealEd.StringTableFactory` | `/Script/Engine.StringTable` | Rule configured |
| `/Script/UnrealEd.StructureFactory` | `/Script/CoreUObject.UserDefinedStruct` | Rule configured |
| `/Script/UnrealEd.SubsurfaceProfileFactory` | `/Script/Engine.SubsurfaceProfile` | Rule configured |
| `/Script/UnrealEd.SubUVAnimationFactory` | `/Script/Engine.SubUVAnimation` | Rule configured |
| `/Script/UnrealEd.Texture2DFactoryNew` | `/Script/Engine.Texture2D` | Rule configured; creation verified |
| `/Script/UnrealEd.TextureRenderTarget2DArrayFactoryNew` | `/Script/Engine.TextureRenderTarget2DArray` | Rule configured; creation verified |
| `/Script/UnrealEd.TextureRenderTargetCubeFactoryNew` | `/Script/Engine.TextureRenderTargetCube` | Rule configured; creation verified |
| `/Script/UnrealEd.TextureRenderTargetFactoryNew` | `/Script/Engine.TextureRenderTarget2D` | Rule configured; creation verified |
| `/Script/UnrealEd.TextureRenderTargetVolumeFactoryNew` | `/Script/Engine.TextureRenderTargetVolume` | Rule configured; creation verified |
| `/Script/UnrealEd.ToonProfileFactory` | `/Script/Engine.ToonProfile` | Rule configured |
| `/Script/UnrealEd.TouchInterfaceFactory` | `/Script/Engine.TouchInterface` | Rule configured |
| `/Script/UnrealEd.UIMaterialFactoryNew` | `/Script/Engine.Material` | Rule configured |
| `/Script/UnrealEd.AnimBankFactory` | `/Script/Engine.AnimBank` | Rule configured; creation verified |
| `/Script/UnrealEd.TransformProviderDataFactory` | `/Script/Engine.TransformProviderData` | Needs review |
| `/Script/UnrealEd.AnimBankDataFactory` | `/Script/Engine.AnimBankData` | Rule configured; creation verified |
| `/Script/UnrealEd.AnimBlueprintFactory` | `/Script/Engine.AnimBlueprint` | Rule configured; creation verified |
| `/Script/UnrealEd.AnimLayerInterfaceFactory` | `/Script/Engine.AnimBlueprint` | Rule configured; creation verified |
| `/Script/UnrealEd.AnimBoneCompressionSettingsFactory` | `/Script/Engine.AnimBoneCompressionSettings` | Rule configured |
| `/Script/UnrealEd.AnimCompositeFactory` | `/Script/Engine.AnimComposite` | TargetSkeleton is not writable through generic properties; needs dedicated path |
| `/Script/UnrealEd.AnimCurveCompressionSettingsFactory` | `/Script/Engine.AnimCurveCompressionSettings` | Rule configured |
| `/Script/UnrealEd.AnimMontageFactory` | `/Script/Engine.AnimMontage` | Rule configured |
| `/Script/UnrealEd.AnimSequenceFactory` | `/Script/Engine.AnimSequence` | Rule configured |
| `/Script/ControlRigEditor.AnimSequenceConverterFactory` | `/Script/Engine.AnimSequence` | Needs review |
| `/Script/UnrealEd.AnimStreamableFactory` | `/Script/Engine.AnimStreamable` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.CompositeCurveTableFactory` | `/Script/Engine.CompositeCurveTable` | Rule configured |
| `/Script/UnrealEd.DataTableFactory` | `/Script/Engine.DataTable` | Rule configured |
| `/Script/UnrealEd.CompositeDataTableFactory` | `/Script/Engine.CompositeDataTable` | Rule configured |
| `/Script/UnrealEd.CurveTableFactory` | `/Script/Engine.CurveTable` | Interpolation selection required; not exposed |
| `/Script/UnrealEd.MeshDeformerCollectionFactory` | `/Script/Engine.MeshDeformerCollection` | Rule configured |
| `/Script/UnrealEd.MirrorDataTableFactory` | `/Script/Engine.MirrorDataTable` | Needs review |
| `/Script/UnrealEd.PackFactory` | `/Script/UnrealEd.PackFactory` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.PhysicsAssetFactory` | `/Script/Engine.PhysicsAsset` | Modal and assigns source mesh; use verified create physics_asset command |
| `/Script/UnrealEd.PoseAssetFactory` | `/Script/Engine.PoseAsset` | Rule configured; creation verified |
| `/Script/UnrealEd.SkeletonFactory` | `/Script/Engine.Skeleton` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.SlateBrushAssetFactory` | `/Script/Engine.SlateBrushAsset` | Rule configured; creation verified |
| `/Script/UnrealEd.SlateWidgetStyleAssetFactory` | `/Script/SlateCore.SlateWidgetStyleAsset` | Creation/save and selected class verified |
| `/Script/UnrealEd.SparseVolumeTextureMaterialFactoryNew` | `/Script/Engine.Material` | Defaults insufficient; inspect import/configuration path |
| `/Script/UnrealEd.Texture2DArrayFactory` | `/Script/Engine.Texture2DArray` | Rule configured; creation verified |
| `/Script/UnrealEd.TextureCubeArrayFactory` | `/Script/Engine.TextureCubeArray` | Rule configured; creation verified |
| `/Script/UnrealEd.VariableFrameStrippingSettingsFactory` | `/Script/Engine.VariableFrameStrippingSettings` | Rule configured |
| `/Script/UnrealEd.VolumeTextureFactory` | `/Script/Engine.VolumeTexture` | Rule configured; creation verified |
| `/Script/UnrealEd.WorldFactory` | `/Script/Engine.World` | Default creation/save/class verified; see batch notes |
| `/Script/BehaviorTreeEditor.BehaviorTreeFactory` | `/Script/AIModule.BehaviorTree` | Rule configured |
| `/Script/BehaviorTreeEditor.BlackboardDataFactory` | `/Script/AIModule.BlackboardData` | Rule configured |
| `/Script/OverlayEditor.BasicOverlaysFactory` | `/Script/Overlay.BasicOverlays` | Defaults insufficient; inspect import/configuration path |
| `/Script/OverlayEditor.ReimportBasicOverlaysFactory` | `/Script/Overlay.BasicOverlays` | Defaults insufficient; inspect import/configuration path |
| `/Script/OverlayEditor.BasicOverlaysFactoryNew` | `/Script/Overlay.BasicOverlays` | Rule configured |
| `/Script/OverlayEditor.LocalizedOverlaysFactoryNew` | `/Script/Overlay.LocalizedOverlays` | Rule configured |
| `/Script/WorldBookmark.WorldBookmarkFactory` | `/Script/WorldBookmark.WorldBookmark` | Rule configured |
| `/Script/WorldPartitionEditor.HLODLayerFactory` | `/Script/Engine.HLODLayer` | Rule configured |
| `/Script/InputEditor.InputMappingContext_Factory` | `/Script/EnhancedInput.InputMappingContext` | Rule configured |
| `/Script/InputEditor.InputAction_Factory` | `/Script/EnhancedInput.InputAction` | Rule configured |
| `/Script/CustomizableObjectEditor.CustomizableObjectFactory` | `/Script/CustomizableObject.CustomizableObject` | Rule configured; creation verified |
| `/Script/CustomizableObjectEditor.CustomizableObjectMacroLibraryFactory` | `/Script/CustomizableObjectEditor.CustomizableObjectMacroLibrary` | Defaults insufficient; inspect import/configuration path |
| `/Script/DataRegistryEditor.DataRegistryFactory` | `/Script/DataRegistry.DataRegistry` | Rule configured; creation verified |
| `/Script/GameplayAbilitiesEditor.GameplayAbilitiesBlueprintFactory` | `/Script/GameplayAbilities.GameplayAbilityBlueprint` | Creation/save and selected class verified |
| `/Script/StateTreeEditorModule.StateTreeFactory` | `/Script/StateTreeModule.StateTree` | Protocol 6 creation/save/schema/root state and invalid schema rejection verified |
| `/Script/WaveTableEditor.WaveTableBankFactory` | `/Script/WaveTable.WaveTableBank` | Rule configured |
| `/Script/MetasoundEditor.MetaSoundBaseFactory` | `None` | Defaults insufficient; inspect import/configuration path |
| `/Script/MetasoundEditor.MetaSoundFactory` | `/Script/MetasoundEngine.MetaSoundPatch` | Rule configured; creation verified |
| `/Script/MetasoundEditor.MetaSoundSourceFactory` | `/Script/MetasoundEngine.MetaSoundSource` | Rule configured; creation verified |
| `/Script/SparseVolumeTexture.SparseVolumeTextureFactory` | `None` | Defaults insufficient; inspect import/configuration path |
| `/Script/UserAssetTagsEditor.TaggedAssetBrowserConfigurationFactory` | `/Script/UserAssetTagsEditor.TaggedAssetBrowserConfiguration` | Rule configured |
| `/Script/NiagaraEditor.NiagaraScriptFactoryNew` | `/Script/Niagara.NiagaraScript` | Abstract factory; use Module, Function or DynamicInput subclasses |
| `/Script/NiagaraEditor.NiagaraModuleScriptFactory` | `/Script/Niagara.NiagaraScript` | Rule configured; creation verified |
| `/Script/NiagaraEditor.NiagaraFunctionScriptFactory` | `/Script/Niagara.NiagaraScript` | Rule configured; creation verified |
| `/Script/NiagaraEditor.NiagaraDynamicInputScriptFactory` | `/Script/Niagara.NiagaraScript` | Rule configured; creation verified |
| `/Script/NiagaraEditor.NiagaraBakerStaticMeshFactoryNew` | `/Script/Engine.StaticMesh` | Defaults insufficient; inspect import/configuration path |
| `/Script/NiagaraEditor.NiagaraDataChannelAssetFactoryNew` | `/Script/Niagara.NiagaraDataChannelAsset` | Rule configured; requires fx.Niagara.DataChannels.Enabled |
| `/Script/NiagaraEditor.NiagaraEffectTypeFactoryNew` | `/Script/Niagara.NiagaraEffectType` | Rule configured |
| `/Script/NiagaraEditor.NiagaraEmitterFactoryNew` | `/Script/Niagara.NiagaraEmitter` | Default creation/save/class verified; see batch notes |
| `/Script/NiagaraEditor.NiagaraParameterCollectionFactoryNew` | `/Script/Niagara.NiagaraParameterCollection` | Rule configured |
| `/Script/NiagaraEditor.NiagaraParameterCollectionInstanceFactoryNew` | `/Script/Niagara.NiagaraParameterCollectionInstance` | Rule configured; creation verified |
| `/Script/NiagaraEditor.NiagaraParameterDefinitionsFactory` | `/Script/NiagaraEditor.NiagaraParameterDefinitions` | Rule configured |
| `/Script/NiagaraEditor.NiagaraSimCacheFactoryNew` | `/Script/Niagara.NiagaraSimCache` | Rule configured |
| `/Script/NiagaraEditor.NiagaraStatelessEmitterTemplateFactoryNew` | `/Script/Niagara.NiagaraStatelessEmitterTemplate` | Rule configured; creation verified |
| `/Script/NiagaraEditor.NiagaraSystemFactoryNew` | `/Script/Niagara.NiagaraSystem` | Default creation/save/class verified; see batch notes |
| `/Script/NiagaraEditor.NiagaraValidationRuleSetFactoryNew` | `/Script/Niagara.NiagaraValidationRuleSet` | Rule configured |
| `/Script/NiagaraEditor.VolumeCacheFactory` | `/Script/Niagara.VolumeCache` | Rule configured; creation verified |
| `/Script/LevelSequenceEditor.LevelSequenceFactoryNew` | `/Script/LevelSequence.LevelSequence` | Rule configured; creation verified |
| `/Script/ChaosCachingEditor.CacheCollectionFactory` | `/Script/ChaosCaching.ChaosCacheCollection` | Defaults insufficient; inspect import/configuration path |
| `/Script/ControlRigEditor.ControlRigAssetFactory` | `/Script/ControlRig.ControlRigRuntimeAsset` | Default creation/save/class verified; requires RigVM.BlueprintIndependentAssets |
| `/Script/ControlRigEditor.ControlRigBlueprintFactory` | `/Script/ControlRigDeveloper.ControlRigBlueprint` | Needs review |
| `/Script/ControlRigEditor.ControlRigShapeLibraryFactory` | `/Script/ControlRig.ControlRigShapeLibrary` | Creation/save/default references verified; required assets checked before creation |
| `/Script/MeshLODToolset.StaticMeshLODGenerationSettingsFactory` | `/Script/MeshLODToolset.StaticMeshLODGenerationSettings` | Rule configured; creation verified |
| `/Script/ToolPresetAsset.InteractiveToolsPresetCollectionAssetFactory` | `/Script/ToolPresetAsset.InteractiveToolsPresetCollectionAsset` | Rule configured; creation and collection label verified |
| `/Script/SkeletalMeshModelingTools.SkeletonFromStaticMeshFactory` | `/Script/Engine.Skeleton` | Needs review |
| `/Script/SkeletalMeshModelingTools.SkeletalMeshFromStaticMeshFactory` | `/Script/Engine.SkeletalMesh` | Needs review |
| `/Script/DataflowEditor.DataflowAssetFactory` | `/Script/DataflowEngine.Dataflow` | Defaults insufficient; inspect import/configuration path |
| `/Script/HairStrandsEditor.GroomBindingFactory` | `/Script/HairStrandsCore.GroomBindingAsset` | Needs review |
| `/Script/HairStrandsEditor.GroomFactory` | `/Script/HairStrandsCore.GroomAsset` | Needs review |
| `/Script/HairStrandsEditor.HairStrandsFactory` | `/Script/HairStrandsCore.GroomAsset` | Defaults insufficient; inspect import/configuration path |
| `/Script/HairStrandsEditor.ReimportGroomCacheFactory` | `/Script/HairStrandsCore.GroomAsset` | Defaults insufficient; inspect import/configuration path |
| `/Script/HairStrandsEditor.ReimportHairStrandsFactory` | `/Script/HairStrandsCore.GroomCache` | Defaults insufficient; inspect import/configuration path |
| `/Script/VariantManagerContentEditor.VariantManagerFactoryNew` | `/Script/VariantManagerContent.LevelVariantSets` | Rule configured |
| `/Script/NNEEditor.NNEModelDataFactory` | `/Script/NNE.NNEModelData` | Defaults insufficient; inspect import/configuration path |
| `/Script/EnvironmentQueryEditor.EnvironmentQueryFactory` | `/Script/AIModule.EnvQuery` | Rule configured |
| `/Script/PCGEditor.PCGBuilderSettingsFactory` | `/Script/PCGEditor.PCGBuilderSettings` | Rule configured |
| `/Script/PCGEditor.PCGComputeSourceFactory` | `/Script/PCG.PCGComputeSource` | Rule configured |
| `/Script/PCGEditor.PCGGraphFactory` | `/Script/PCG.PCGGraph` | Rule configured |
| `/Script/PCGEditor.PCGGraphInstanceFactory` | `/Script/PCG.PCGGraphInstance` | Protocol 4 creation, save and parent readback verified |
| `/Script/SynthesisEditor.AudioImpulseResponseFactory` | `/Script/Synthesis.AudioImpulseResponse` | Defaults insufficient; inspect import/configuration path |
| `/Script/SynthesisEditor.ModularSynthPresetBankFactory` | `/Script/Synthesis.ModularSynthPresetBank` | Rule configured; creation verified |
| `/Script/SynthesisEditor.MonoWaveTableSynthPresetFactory` | `/Script/Synthesis.MonoWaveTableSynthPreset` | Rule configured; creation verified |
| `/Script/EditableComputeGraphEditor.EditableComputeGraphFactory` | `/Script/EditableComputeGraph.EditableComputeGraph` | Rule configured; creation verified |
| `/Script/AlembicImporter.AlembicImportFactory` | `None` | Defaults insufficient; inspect import/configuration path |
| `/Script/Paper2DEditor.PaperSpriteAtlasFactory` | `/Script/Paper2D.PaperSpriteAtlas` | Conditional rule; disabled setting rejection verified; user chose to keep disabled |
| `/Script/Paper2DEditor.PaperFlipbookFactory` | `/Script/Paper2D.PaperFlipbook` | Rule configured |
| `/Script/Paper2DEditor.PaperSpriteFactory` | `/Script/Paper2D.PaperSprite` | Rule configured; creation verified |
| `/Script/Paper2DEditor.PaperTileMapFactory` | `/Script/Paper2D.PaperTileMap` | Rule configured; creation verified |
| `/Script/Paper2DEditor.PaperTileMapPromotionFactory` | `/Script/Paper2D.PaperTileMap` | Defaults insufficient; inspect import/configuration path |
| `/Script/Paper2DEditor.PaperTileSetFactory` | `/Script/Paper2D.PaperTileSet` | Rule configured |
| `/Script/Paper2DEditor.TileSheetPaddingFactory` | `/Script/Engine.Texture` | Defaults insufficient; inspect import/configuration path |
| `/Script/PaperSpriteSheetImporter.PaperSpriteSheetImportFactory` | `/Script/PaperSpriteSheetImporter.PaperSpriteSheet` | Defaults insufficient; inspect import/configuration path |
| `/Script/PaperSpriteSheetImporter.PaperSpriteSheetReimportFactory` | `/Script/PaperSpriteSheetImporter.PaperSpriteSheet` | Defaults insufficient; inspect import/configuration path |
| `/Script/PaperTiledImporter.PaperTiledImporterFactory` | `/Script/Paper2D.PaperTileMap` | Defaults insufficient; inspect import/configuration path |
| `/Script/MetaHumanSDKEditor.MetaHumanPackageFactory` | `/Script/CoreUObject.Object` | Defaults insufficient; inspect import/configuration path |
| `/Script/ChaosSolverEditor.ChaosSolverFactory` | `/Script/ChaosSolverEngine.ChaosSolver` | Rule configured |
| `/Script/GeometryCollectionEditor.GeometryCollectionCacheFactory` | `/Script/GeometryCollectionEngine.GeometryCollectionCache` | Defaults insufficient; inspect import/configuration path |
| `/Script/GeometryCollectionEditor.GeometryCollectionFactory` | `/Script/GeometryCollectionEngine.GeometryCollection` | Needs review |
| `/Script/AnimationSharingEd.AnimationSharingSetupFactory` | `/Script/AnimationSharing.AnimationSharingSetup` | Rule configured |
| `/Script/NamingTokensUncookedOnly.NamingTokensFactory` | `/Script/NamingTokens.NamingTokens` | Default creation/save verified; see current verification notes |
| `/Script/NamingTokensEditor.EditorUtilityNamingTokensFactory` | `/Script/NamingTokensEditor.EditorUtilityNamingTokens` | Default creation/save verified; see current verification notes |
| `/Script/InterchangeEditorPipelines.InterchangeBlueprintPipelineBaseFactory` | `/Script/InterchangeEngine.InterchangeBlueprintPipelineBase` | Default creation/save/class verified; see batch notes |
| `/Script/InterchangeEditorPipelines.InterchangeEditorBlueprintPipelineBaseFactory` | `/Script/InterchangeEditorPipelines.InterchangeEditorBlueprintPipelineBase` | Default creation/save/class verified; see batch notes |
| `/Script/InterchangeEditorPipelines.InterchangePipelineBaseFactory` | `/Script/InterchangeCore.InterchangePipelineBase` | Needs review |
| `/Script/InterchangeEditorPipelines.InterchangePythonPipelineAssetFactory` | `/Script/InterchangeEngine.InterchangePythonPipelineAsset` | Needs review |
| `/Script/ACLPluginEditor.AnimationCompressionLibraryDatabaseFactory` | `/Script/ACLPlugin.AnimationCompressionLibraryDatabase` | Rule configured |
| `/Script/EaseCurveTool.EaseCurveLibraryFactory` | `/Script/EaseCurveTool.EaseCurveLibrary` | Rule configured |
| `/Script/ConsoleVariablesEditor.ConsoleVariablesEditorFactory` | `/Script/ConsoleVariablesEditorRuntime.ConsoleVariablesAsset` | Rule configured |
| `/Script/MaterialAssetWizard.MaterialFactoryWithAssetWizardBase` | `None` | Defaults insufficient; inspect import/configuration path |
| `/Script/MaterialAssetWizard.MaterialFactoryWithAssetWizard` | `/Script/Engine.Material` | Needs review |
| `/Script/MaterialAssetWizard.MaterialInstanceConstantFactoryWithAssetWizard` | `/Script/Engine.MaterialInstanceConstant` | Needs review |
| `/Script/ObjectMixerEditor.ObjectMixerBlueprintFilterFactory` | `/Script/Engine.Blueprint` | Default creation/save/class verified; see batch notes |
| `/Script/SpeedTreeImporter.SpeedTreeImportFactory` | `/Script/Engine.StaticMesh` | Defaults insufficient; inspect import/configuration path |
| `/Script/SpeedTreeImporter.ReimportSpeedTreeFactory` | `/Script/Engine.StaticMesh` | Defaults insufficient; inspect import/configuration path |
| `/Script/UMGWidgetPreview.WidgetPreviewFactory` | `/Script/UMGWidgetPreview.WidgetPreview` | Rule configured; creation verified |
| `/Script/MediaPlayerEditor.FileMediaSourceFactoryNew` | `/Script/MediaAssets.FileMediaSource` | Rule configured |
| `/Script/MediaPlayerEditor.MediaPlayerFactoryNew` | `/Script/MediaAssets.MediaPlayer` | Rule configured; creation verified |
| `/Script/MediaPlayerEditor.MediaPlaylistFactoryNew` | `/Script/MediaAssets.MediaPlaylist` | Rule configured |
| `/Script/MediaPlayerEditor.MediaTextureFactoryNew` | `/Script/MediaAssets.MediaTexture` | Rule configured; creation verified |
| `/Script/MediaPlayerEditor.PlatformMediaSourceFactoryNew` | `/Script/MediaAssets.PlatformMediaSource` | Rule configured |
| `/Script/MediaPlayerEditor.StreamMediaSourceFactoryNew` | `/Script/MediaAssets.StreamMediaSource` | Rule configured |
| `/Script/InterchangeTestEditor.InterchangeImportTestPlanFactory` | `/Script/InterchangeTests.InterchangeImportTestPlan` | Rule configured |
| `/Script/AudioSynesthesiaEditor.AudioSynesthesiaNRTFactory` | `/Script/AudioSynesthesia.AudioSynesthesiaNRT` | Creation/save and selected class verified |
| `/Script/AudioSynesthesiaEditor.AudioSynesthesiaNRTSettingsFactory` | `/Script/AudioSynesthesia.AudioSynesthesiaNRTSettings` | Creation/save and selected class verified |
| `/Script/AudioSynesthesiaEditor.AudioSynesthesiaSettingsFactory` | `/Script/AudioSynesthesia.AudioSynesthesiaSettings` | Creation/save and selected class verified |
| `/Script/ResonanceAudioEditor.ResonanceAudioReverbPluginPresetFactory` | `/Script/ResonanceAudio.ResonanceAudioReverbPluginPreset` | Rule configured |
| `/Script/ResonanceAudioEditor.ResonanceAudioSpatializationSourceSettingsFactory` | `/Script/ResonanceAudio.ResonanceAudioSpatializationSourceSettings` | Rule configured |
| `/Script/WaterEditor.WaterWavesAssetFactory` | `/Script/Water.WaterWavesAsset` | Rule configured; creation verified |
| `/Script/TemplateSequenceEditor.CameraAnimationSequenceFactoryNew` | `/Script/TemplateSequence.CameraAnimationSequence` | Rule configured; creation verified |
| `/Script/TemplateSequenceEditor.TemplateSequenceFactoryNew` | `/Script/TemplateSequence.TemplateSequence` | Creation/save and native postconditions or parent validation verified |
| `/Script/OptimusEditor.OptimusDeformerFactory` | `/Script/OptimusCore.OptimusDeformer` | Rule configured; creation verified |
| `/Script/OptimusEditor.OptimusSourceFactory` | `/Script/OptimusCore.OptimusSource` | Rule configured |
| `/Script/IKRigEditor.IKRetargetFactory` | `/Script/IKRig.IKRetargeter` | Rule configured |
| `/Script/IKRigEditor.IKRigDefinitionFactory` | `/Script/IKRig.IKRigDefinition` | Rule configured |
| `/Script/PhysicsControlEditor.PhysicsControlAssetFactory` | `/Script/PhysicsControl.PhysicsControlAsset` | Rule configured |
| `/Script/GameplayCamerasEditor.CameraAssetFactory` | `/Script/GameplayCameras.CameraAsset` | Creation/save and native postconditions or parent validation verified |
| `/Script/GameplayCamerasEditor.CameraRigAssetFactory` | `/Script/GameplayCameras.CameraRigAsset` | Rule configured; creation verified |
| `/Script/GameplayCamerasEditor.CameraRigProxyAssetFactory` | `/Script/GameplayCameras.CameraRigProxyAsset` | Rule configured |
| `/Script/GameplayCamerasEditor.CameraShakeAssetFactory` | `/Script/GameplayCameras.CameraShakeAsset` | Rule configured; creation verified |
| `/Script/GameplayCamerasEditor.CameraVariableCollectionFactory` | `/Script/GameplayCameras.CameraVariableCollection` | Rule configured |
| `/Script/AndroidMediaEditor.AndroidFileMediaSourceFactory` | `/Script/MediaAssets.FileMediaSource` | Defaults insufficient; inspect import/configuration path |
| `/Script/ImgMediaEditor.ImgMediaSourceFactory` | `/Script/ImgMedia.ImgMediaSource` | Defaults insufficient; inspect import/configuration path |
| `/Script/ImgMediaEditor.ImgMediaSourceFactoryNew` | `/Script/ImgMedia.ImgMediaSource` | Rule configured |
| `/Script/ImgMediaEditor.TmvFileMediaSourceFactory` | `/Script/MediaAssets.FileMediaSource` | Defaults insufficient; inspect import/configuration path |
| `/Script/AvfMediaEditor.AvfFileMediaSourceFactory` | `/Script/MediaAssets.FileMediaSource` | Defaults insufficient; inspect import/configuration path |
| `/Script/WmfMediaEditor.WmfFileMediaSourceFactory` | `/Script/MediaAssets.FileMediaSource` | Defaults insufficient; inspect import/configuration path |
| `/Script/WebMMediaEditor.WebMPlatFileMediaSourceFactory` | `/Script/MediaAssets.FileMediaSource` | Defaults insufficient; inspect import/configuration path |

## Reviewed simple factories

All 16 below were created and saved in `/Game/UnrealBPDemo/SimpleFactories`; their actual asset classes were read back and matched the catalog.

These factory implementations were inspected for their construction and FactoryCreateNew paths. No caller-supplied dependency is required. Assets are created with engine defaults; this does not configure playback sources, AI logic, or effect content.

- `/Script/MediaPlayerEditor.MediaPlaylistFactoryNew`: `Plugins/Media/MediaPlayerEditor/Source/MediaPlayerEditor/Private/Factories/MediaPlaylistFactoryNew.cpp`
- `/Script/MediaPlayerEditor.PlatformMediaSourceFactoryNew`: `Plugins/Media/MediaPlayerEditor/Source/MediaPlayerEditor/Private/Factories/PlatformMediaSourceFactoryNew.cpp`
- `/Script/MediaPlayerEditor.StreamMediaSourceFactoryNew`: `Plugins/Media/MediaPlayerEditor/Source/MediaPlayerEditor/Private/Factories/StreamMediaSourceFactoryNew.cpp`
- `/Script/MediaPlayerEditor.FileMediaSourceFactoryNew`: `Plugins/Media/MediaPlayerEditor/Source/MediaPlayerEditor/Private/Factories/FileMediaSourceFactoryNew.cpp`
- `/Script/AudioEditor.SoundMixFactory`: `Source/Editor/AudioEditor/Private/Factories/SoundMixFactory.cpp`
- `/Script/AudioEditor.ReverbEffectFactory`: `Source/Editor/AudioEditor/Private/Factories/ReverbEffectFactory.cpp`
- `/Script/AudioEditor.SoundClassFactory`: `Source/Editor/AudioEditor/Private/Factories/SoundClassFactory.cpp`
- `/Script/AudioEditor.SoundAttenuationFactory`: `Source/Editor/AudioEditor/Private/Factories/SoundAttenuationFactory.cpp`
- `/Script/AudioEditor.AudioBusFactory`: `Source/Editor/AudioEditor/Private/Factories/AudioBusFactory.cpp`
- `/Script/AudioEditor.SoundConcurrencyFactory`: `Source/Editor/AudioEditor/Private/Factories/SoundConcurrencyFactory.cpp`
- `/Script/AudioEditor.DialogueVoiceFactory`: `Source/Editor/AudioEditor/Private/Factories/DialogueVoiceFactory.cpp`
- `/Script/ImgMediaEditor.ImgMediaSourceFactoryNew`: `Plugins/Media/ImgMedia/Source/ImgMediaEditor/Private/Factories/ImgMediaSourceFactoryNew.cpp`
- `/Script/BehaviorTreeEditor.BehaviorTreeFactory`: `Source/Editor/BehaviorTreeEditor/Private/BehaviorTreeFactory.cpp`
- `/Script/BehaviorTreeEditor.BlackboardDataFactory`: `Source/Editor/BehaviorTreeEditor/Private/BlackboardDataFactory.cpp`
- `/Script/NiagaraEditor.NiagaraValidationRuleSetFactoryNew`: `Plugins/FX/Niagara/Source/NiagaraEditor/Private/NiagaraValidationRuleSetFactoryNew.cpp`
- `/Script/NiagaraEditor.NiagaraEffectTypeFactoryNew`: `Plugins/FX/Niagara/Source/NiagaraEditor/Private/NiagaraEffectTypeFactoryNew.cpp`

## Second simple group

All 15 were created, saved and class-verified in `/Game/UnrealBPDemo/SimpleFactories`. The animation curve compression factory’s codec was also read back.

Input factories support their base classes only; custom subtype selection is not exposed. VirtualTextureBuilder creates an unbuilt asset, NiagaraSimCache an empty cache, and PaperFlipbook an empty animation. These are creation rules, not content generation.

- `/Script/VirtualTexturingEditor.VirtualTextureBuilderFactory`: `Source/Editor/VirtualTexturingEditor/Private/VirtualTextureBuilderFactory.cpp`
- `/Script/VirtualTexturingEditor.RuntimeVirtualTextureFactory`: `Source/Editor/VirtualTexturingEditor/Private/RuntimeVirtualTextureFactory.cpp`
- `/Script/DataLayerEditor.DataLayerFactory`: `Source/Editor/DataLayerEditor/Private/DataLayer/DataLayerFactory.cpp`
- `/Script/WorldPartitionEditor.HLODLayerFactory`: `Source/Editor/WorldPartitionEditor/Private/WorldPartition/HLOD/HLODLayerFactory.cpp`
- `/Script/UnrealEd.AnimBoneCompressionSettingsFactory`: `Source/Editor/UnrealEd/Private/Factories/AnimBoneCompressionSettingsFactory.cpp`
- `/Script/UnrealEd.AnimCurveCompressionSettingsFactory`: `Source/Editor/UnrealEd/Private/Factories/AnimCurveCompressionSettingsFactory.cpp`
- `/Script/UnrealEd.VariableFrameStrippingSettingsFactory`: `Source/Editor/UnrealEd/Private/Factories/VariableFrameStrippingSettingsFactory.cpp`
- `/Script/FoliageEdit.LandscapeGrassTypeFactory`: `Source/Editor/FoliageEdit/Private/LandscapeGrassTypeFactory.cpp`
- `/Script/NiagaraEditor.NiagaraSimCacheFactoryNew`: `Plugins/FX/Niagara/Source/NiagaraEditor/Private/NiagaraSimCacheFactoryNew.cpp`
- `/Script/NiagaraEditor.NiagaraParameterDefinitionsFactory`: `Plugins/FX/Niagara/Source/NiagaraEditor/Private/NiagaraParameterDefinitionsFactory.cpp`
- `/Script/Paper2DEditor.PaperFlipbookFactory`: `Plugins/2D/Paper2D/Source/Paper2DEditor/Private/PaperFlipbookFactory.cpp`
- `/Script/InputEditor.InputAction_Factory`: `Plugins/EnhancedInput/Source/InputEditor/Private/EnhancedInputEditorModule.cpp`
- `/Script/InputEditor.InputMappingContext_Factory`: `Plugins/EnhancedInput/Source/InputEditor/Private/EnhancedInputEditorModule.cpp`
- `/Script/UnrealEd.StringTableFactory`: `Source/Editor/UnrealEd/Private/Factories/EditorFactories.cpp`
- `/Script/UnrealEd.MaterialParameterCollectionFactoryNew`: `Source/Editor/UnrealEd/Private/Factories/EditorFactories.cpp`

## Profile and feedback group

All 12 were created, saved and class-verified in `/Game/UnrealBPDemo/SimpleFactories`.

Source reviewed: `Source/Editor/UnrealEd/Private/Factories/EditorFactories.cpp`. No creation options are exposed for these default assets. SubUV textures, haptic wave data and touch controls are not populated. Profile GUIDs and profile defaults are initialized by the native factories.

- `/Script/UnrealEd.ObjectLibraryFactory`
- `/Script/UnrealEd.ForceFeedbackAttenuationFactory`
- `/Script/UnrealEd.ForceFeedbackEffectFactory`
- `/Script/UnrealEd.HapticFeedbackEffectCurveFactory`
- `/Script/UnrealEd.HapticFeedbackEffectBufferFactory`
- `/Script/UnrealEd.HapticFeedbackEffectSoundWaveFactory`
- `/Script/UnrealEd.SubsurfaceProfileFactory`
- `/Script/UnrealEd.SpecularProfileFactory`
- `/Script/UnrealEd.NeuralProfileFactory`
- `/Script/UnrealEd.ToonProfileFactory`
- `/Script/UnrealEd.TouchInterfaceFactory`
- `/Script/UnrealEd.SubUVAnimationFactory`

## Collection and query group

All eight were created, saved and class-verified in `/Game/UnrealBPDemo/SimpleFactories`.

Creates default assets only; no query options, overlays, animation-sharing skeletons, variants or collection parameters are populated. Basic/Localized Overlays are intentionally absent from the native New menu but have valid create-new factories.

- `/Script/UnrealEd.CompositeCurveTableFactory`: `Source/Editor/UnrealEd/Private/Factories/CompositeCurveTableFactory.cpp`
- `/Script/EnvironmentQueryEditor.EnvironmentQueryFactory`: `Plugins/AI/EnvironmentQueryEditor/Source/EnvironmentQueryEditor/Private/EnvironmentQueryFactory.cpp`
- `/Script/OverlayEditor.LocalizedOverlaysFactoryNew`: `Source/Editor/OverlayEditor/Private/Factories/LocalizedOverlaysFactoryNew.cpp`
- `/Script/OverlayEditor.BasicOverlaysFactoryNew`: `Source/Editor/OverlayEditor/Private/Factories/BasicOverlaysFactoryNew.cpp`
- `/Script/AnimationSharingEd.AnimationSharingSetupFactory`: `Plugins/Developer/AnimationSharing/Source/AnimationSharingEd/Private/AnimationSharingSetupFactory.cpp`
- `/Script/NiagaraEditor.NiagaraParameterCollectionFactoryNew`: `Plugins/FX/Niagara/Source/NiagaraEditor/Private/NiagaraParameterCollectionFactoryNew.cpp`
- `/Script/VariantManagerContentEditor.VariantManagerFactoryNew`: `Plugins/Enterprise/VariantManagerContent/Source/VariantManagerContentEditor/Private/VariantManagerFactoryNew.cpp`
- `/Script/AudioEditor.SoundSourceBusFactory`: `Source/Editor/AudioEditor/Private/Factories/SoundSourceBusFactory.cpp`

## Blueprint libraries and material specializations

All six were created and saved. Three Blueprint compile calls completed; registry tags verified their Blueprint types and parents. UI Material domain was MD_UI; both layer asset classes matched. Direct BlueprintType/status property reads are not exposed; runtime behavior was not tested.

Source: `Source/Editor/UnrealEd/Private/Factories/EditorFactories.cpp`. No options: Function Library uses BlueprintFunctionLibrary, Interface uses Interface, Macro Library uses Actor as its factory-defined parent. Custom parents are not exposed. The function-library config gate still participates through create_new. UI Material and layer factories initialize their native domain/usage.

- `/Script/UnrealEd.BlueprintFunctionLibraryFactory`
- `/Script/UnrealEd.BlueprintInterfaceFactory`
- `/Script/UnrealEd.BlueprintMacroFactory`
- `/Script/UnrealEd.UIMaterialFactoryNew`
- `/Script/UnrealEd.MaterialFunctionMaterialLayerFactory`
- `/Script/UnrealEd.MaterialFunctionMaterialLayerBlendFactory`

## PCG, rig and helper group

All seven were created, saved and class-verified in `/Game/UnrealBPDemo/SimpleFactories`.

Default creation only: PCG Graph has no selected template, IK assets have no rig/mesh configuration, Console Variables has no commands, and Paper Tile Set has no assigned texture. PCG generation, retargeting and texture assignment are not part of these rules.

- `/Script/PCGEditor.PCGComputeSourceFactory`: `Plugins/PCG/Source/PCGEditor/Private/Factories/PCGComputeSourceFactory.cpp`
- `/Script/PCGEditor.PCGBuilderSettingsFactory`: `Plugins/PCG/Source/PCGEditor/Private/Factories/PCGBuilderSettingsFactory.cpp`
- `/Script/PCGEditor.PCGGraphFactory`: `Plugins/PCG/Source/PCGEditor/Private/PCGGraphFactory.cpp`
- `/Script/IKRigEditor.IKRetargetFactory`: `Plugins/Animation/IKRig/Source/IKRigEditor/Private/RetargetEditor/IKRetargetFactory.cpp`
- `/Script/IKRigEditor.IKRigDefinitionFactory`: `Plugins/Animation/IKRig/Source/IKRigEditor/Private/RigEditor/IKRigDefinitionFactory.cpp`
- `/Script/ConsoleVariablesEditor.ConsoleVariablesEditorFactory`: `Plugins/Editor/ConsoleVariablesEditor/Source/ConsoleVariablesEditor/Private/Factories/ConsoleVariablesEditorFactory.cpp`
- `/Script/Paper2DEditor.PaperTileSetFactory`: `Plugins/2D/Paper2D/Source/Paper2DEditor/Private/PaperTileSetFactory.cpp`

## Additional helper factories

All 16 were created, saved and class-verified.

These create default assets; collections, bookmarks, solver settings, shader sources and audio presets still need project content/configuration.

- `/Script/VirtualTexturingEditor.MaterialCacheVirtualTextureTagFactory`: `Source/Editor/VirtualTexturingEditor/Private/MaterialCacheVirtualTextureTagFactory.cpp`
- `/Script/WorldBookmark.WorldBookmarkFactory`: `Source/Editor/WorldBookmark/Private/WorldBookmark/WorldBookmarkFactory.cpp`
- `/Script/UnrealEd.MeshDeformerCollectionFactory`: `Source/Editor/UnrealEd/Private/Factories/MeshDeformerCollectionFactory.cpp`
- `/Script/PhysicsControlEditor.PhysicsControlAssetFactory`: `Plugins/Animation/PhysicsControl/Source/PhysicsControlEditor/Private/PhysicsControlAssetFactory.cpp`
- `/Script/UMGEditor.SlateVectorArtDataFactory`: `Source/Editor/UMGEditor/Private/SlateVectorArtDataFactory.cpp`
- `/Script/UserAssetTagsEditor.TaggedAssetBrowserConfigurationFactory`: `Source/Editor/UserAssetTagsEditor/Private/AssetFactories/TaggedAssetBrowserConfigurationFactory.cpp`
- `/Script/OptimusEditor.OptimusSourceFactory`: `Plugins/Animation/DeformerGraph/Source/OptimusEditor/Private/OptimusSourceFactory.cpp`
- `/Script/EaseCurveTool.EaseCurveLibraryFactory`: `Plugins/Animation/EaseCurveTool/Source/EaseCurveTool/Private/EaseCurveLibraryFactory.cpp`
- `/Script/GameplayCamerasEditor.CameraVariableCollectionFactory`: `Plugins/Cameras/GameplayCameras/Source/GameplayCamerasEditor/Private/Factories/CameraVariableCollectionFactory.cpp`
- `/Script/GameplayCamerasEditor.CameraRigProxyAssetFactory`: `Plugins/Cameras/GameplayCameras/Source/GameplayCamerasEditor/Private/Factories/CameraRigProxyAssetFactory.cpp`
- `/Script/InterchangeTestEditor.InterchangeImportTestPlanFactory`: `Plugins/Tests/InterchangeTests/Source/InterchangeTestEditor/Private/InterchangeImportTestPlanFactory.cpp`
- `/Script/ACLPluginEditor.AnimationCompressionLibraryDatabaseFactory`: `Plugins/Animation/ACLPlugin/Source/ACLPluginEditor/Private/AnimationCompressionLibraryDatabaseFactory.cpp`
- `/Script/ResonanceAudioEditor.ResonanceAudioSpatializationSourceSettingsFactory`: `Plugins/Runtime/ResonanceAudio/Source/ResonanceAudioEditor/Private/ResonanceAudioSpatializationSourceSettingsFactory.cpp`
- `/Script/ResonanceAudioEditor.ResonanceAudioReverbPluginPresetFactory`: `Plugins/Runtime/ResonanceAudio/Source/ResonanceAudioEditor/Private/ResonanceAudioReverbPluginPresetFactory.cpp`
- `/Script/WaveTableEditor.WaveTableBankFactory`: `Plugins/Runtime/WaveTable/Source/WaveTableEditor/Private/WaveTableBankFactory.cpp`
- `/Script/ChaosSolverEditor.ChaosSolverFactory`: `Plugins/Experimental/ChaosSolverPlugin/Source/ChaosSolverEditor/Private/Chaos/ChaosSolverFactory.cpp`

## Dependency-based creation

AnimCompositeFactory has a native-backed `targetSkeleton` rule (98 reviewed rules). UnrealBPBridge compiled successfully with SpaceGovernorEditor / UE 5.8.2 on Mac and loaded after an editor restart; native protocol version 1 was verified. `/Game/UnrealBPDemo/FactoryCommands/AC_BridgeDemo` was created through the DSL and saved. Its AnimComposite class and UE4 Mannequin skeleton reference were read back successfully. Passing an AnimComposite as targetSkeleton was rejected before creation, and `AC_InvalidBridgeDemo` was confirmed absent. This creates an empty composite; animation segments are not configured. The catalog marks the factory unavailable while the bridge is not loaded.

Composite DataTable and five new animation types were created and saved. Row struct and all skeleton references were read back. Existing AnimSequenceFactory was also verified with the project UE4 Mannequin skeleton. Invalid Composite DataTable row struct was rejected before creation.

CompositeDataTableFactory requires struct and shares native/UserDefinedStruct row validation with DataTableFactory. Parent tables are not assigned. BlendSpaceFactoryNew, BlendSpaceFactory1D, AimOffsetBlendSpaceFactoryNew, AimOffsetBlendSpaceFactory1D and AnimMontageFactory require targetSkeleton; source animation, preview mesh and animation samples are not exposed. Sources: UnrealEd EditorFactories.cpp, AnimMontageFactory.cpp, CompositeDataTableFactory.cpp and DataTableFactory.cpp.

## Audio and foliage default creation

Nine additional factory rules bring the reviewed total to 107. All nine assets were created through the DSL under `/Game/UnrealBPDemo/SimpleFactories`, saved successfully and read back with the exact expected class. Rules expose no options: sound inputs, dialogue voices, effects, submix routing/format, foliage meshes and actor classes are not configured by this batch.

Reviewed UE 5.8 sources: `Source/Editor/AudioEditor/Private/Factories/SoundCueFactoryNew.cpp`, `DialogueWaveFactory.cpp`, `SoundSourceEffectFactory.cpp`, `SoundSubmixFactory.cpp`; `Source/Editor/FoliageEdit/Private/FoliageTypeFactory.cpp`. These native default creation paths require no ConfigureProperties dialog or new bridge operation.

## Media, rendering, animation and graph creation

32 more factories were created, saved and read back with their expected classes; 139 creation rules have live positive verification. A 140th rule, DataAssetFactory, awaits native protocol 2 activation and live verification.

- MediaPlayerFactoryNew, MediaTextureFactoryNew, VolumeCacheFactory, LevelSequenceFactoryNew and CameraAnimationSequenceFactoryNew. The camera sequence has a movie scene and one CineCameraActor spawnable. Media Player does not create an extra video texture; media content, volume cache source and animation keys are not assigned.
- Texture2DFactoryNew (native 256x256 white source), PhysicalMaterialFactoryNew, PhysicalMaterialMaskFactory, CanvasRenderTarget2DFactoryNew, CurveLinearColorAtlasFactory and RenderTarget 2D/2DArray/Cube/Volume factories. Native default sizes/formats only; texture import, custom material subclasses and masks are not configured.
- CameraRigAssetFactory, CameraShakeAssetFactory, OptimusDeformerFactory, StaticMeshLODGenerationSettingsFactory, ModularSynthPresetBankFactory and MonoWaveTableSynthPresetFactory. Factory defaults only; no working camera/deformer/synth behavior is claimed.
- Three AnimSequenceTransformProvider factories (LayerStack, SequenceList, BlendSpaceList), AnimBankDataFactory, AnimBankFactory and PoseAssetFactory. AnimBank requires targetSkeleton. PoseAsset requires sourceAnimation with a skeleton; Aim_Space_Hip produced 87 poses with the expected UE4 Mannequin skeleton. Custom pose names are not exposed.
- EditableComputeGraphFactory, DataRegistryFactory, CustomizableObjectFactory, PaperSpriteFactory and PaperTileMapFactory. Default creation only; graph content, registry schema/sources, sprite texture and tile set are not assigned.
- NiagaraStatelessEmitterTemplateFactoryNew requires `fx.NiagaraStateless.AllowTemplateCreation` to be enabled. Disabled creation was rejected and no asset existed; after explicit user approval the session-only cvar was enabled and asset creation/save/class verification passed. Unreal marks this experimental with potential data loss. The plugin does not silently enable it or persist it to project config.

Sources reviewed in UE 5.8: UnrealEd/Private/Factories/EditorFactories.cpp, AnimBankFactory.cpp, TransformProviderFactory.cpp and PoseAssetFactory.cpp; AnimGraph/Private/AnimSequenceTransformProviderFactories.cpp; corresponding MediaPlayerEditor, LevelSequenceEditor, TemplateSequenceEditor, NiagaraEditor, GameplayCamerasEditor, OptimusEditor, MeshLODToolset, SynthesisEditor, EditableComputeGraphEditor, DataRegistryEditor, CustomizableObjectEditor and Paper2DEditor factory implementations.

DataAssetFactory requires dataAssetClass. Native protocol 2 duplicates the existing Data Asset class picker's exact exclusion flags (Abstract, Deprecated, NewerVersionExists, HideDropDown) and checks the DataAsset base class before creation. Build passed; active editor still has protocol 1. Composite supports protocol 1 and 2 and remains available. Data Asset must not be counted as verified yet.

GeometryCollectionFactory consumes selected editor actors/assets and opens a dataflow template picker; it is not safe to label it default empty creation. StateTree requires an explicit schema. TemplateSequence requires an explicit root class and valid spawnable creation. These remain outside the reviewed rules.

Protocol 2 activation follow-up: the first restart still loaded protocol 1 because the earlier hot-reload build left the module manifest pointing at `-0001.dylib`. Rebuilding with `-NoHotReloadFromIDE` succeeded and UnrealBuildTool regenerated the manifest to use `libUnrealEditor-UnrealBPBridge.dylib`. Another editor restart is required before Data Asset live verification. No asset creation was attempted with the outdated validator.

## Current verification: 154 passed, one native activation pending

155 reviewed rules are configured. DataAssetFactory is now verified on native protocol 2: `DA_BridgeDemo` was created and saved as AnimSequenceTransformProviderSequenceList; abstract DataAsset was rejected before creation and `DA_AbstractRejected` was confirmed absent.

WidgetBlueprintFactory and EditorUtilityWidgetBlueprintFactory created `WBP_FactoryDemo` and `EUW_FactoryDemo` under FactoryCommands. Both were compiled and saved; actual Blueprint classes and generated UserWidget/EditorUtilityWidget inheritance were verified. Parent/root overrides are not exposed; native project settings govern root widget behavior.

Seven new default factories were created/saved/class-verified under SimpleFactories: MaterialFunctionInstanceFactory, MaterialFunctionMaterialLayerInstanceFactory, MaterialFunctionMaterialLayerBlendInstanceFactory, SlateBrushAssetFactory, Texture2DArrayFactory, TextureCubeArrayFactory and VolumeTextureFactory. Function instances have no parent, Slate Brush has no source texture, arrays have no source elements, and Volume Texture uses the factory's one-texel default. Texture2DArray requires the existing `r.AllowTexture2DArrayCreation` console gate (tested with value 1). Source: UnrealEd/Private/Factories/EditorFactories.cpp and the corresponding texture/brush factory .cpp files.

Five further default factories were created/saved/class-verified: MetaSoundFactory, MetaSoundSourceFactory, WaterWavesAssetFactory, WidgetPreviewFactory and NiagaraParameterCollectionInstanceFactoryNew. MetaSound initializes/registers its native document; no playable audio graph is claimed. Preview has no widget assigned; Niagara collection instance has no parent assigned. Sources: MetasoundFactory.cpp and MetasoundEditorSubsystem.cpp, WaterWavesAssetFactory.cpp, WidgetPreviewFactory.cpp, NiagaraParameterCollectionFactoryNew.cpp.

PreviewMeshCollectionFactory requires currentSkeleton. Its reflected weak-reference field is not writable through Python; native protocol 3 adds a typed factory setter while keeping the existing creation helper. Normal -NoHotReloadFromIDE build succeeded and the manifest references libUnrealEditor-UnrealBPBridge.dylib. Active editor is still on protocol 2, so live creation is pending; the catalog correctly disables this factory while Data Asset and Composite stay available.

## Current verification: 160 rules passed

Native protocol 3 loaded successfully. PreviewMeshCollectionFactory created and saved `/Game/UnrealBPDemo/FactoryCommands/PMC_BridgeDemo`; its PreviewMeshCollection class and exact UE4 Mannequin skeleton were read back.

AnimBlueprintFactory requires targetSkeleton and uses the native AnimInstance parent. AnimLayerInterfaceFactory exposes no options and creates BPTYPE_Interface with AnimLayerInterface parent, without a target skeleton. ABP_FactoryDemo and ALI_FactoryDemo were created, compiled and saved; their AnimBlueprint class, generated classes, skeleton and parent/interface registry tags were verified. Source: UnrealEd/Private/Factories/AnimBlueprintFactory.cpp and its header. Template and custom parent/preview mesh overrides are not exposed.

NiagaraModuleScriptFactory, NiagaraFunctionScriptFactory and NiagaraDynamicInputScriptFactory were created/saved with exact NiagaraScript classes. Saved Usage tags were respectively Module, Function and DynamicInput, and ClassUsageList showed the initialized node types. Native factory behavior uses project-configured default script templates or procedurally initializes a graph; no custom effect behavior or runtime execution is claimed. Usage is protected in Python; verification used saved registry tags. NiagaraScriptFactoryNew itself is ABSTRACT and is intentionally excluded from rules (a failed instantiation produced no asset). Source: NiagaraScriptFactory.cpp and NiagaraScriptFactoryNew.h.

PhysicsAssetFactory is not a dialog-free path: it opens the body-generation dialog and then assigns the result to the source skeletal mesh. Existing PhysicsAssetToolset.CreateFromMesh has a bAssignToMesh parameter and generates without a dialog, but fixes the output path beside the mesh with a _PhysicsAsset suffix. User preference for default assignment is pending; no Physics Asset command or rule has been added and no source mesh assignment was changed.

### Current verification: 163 rules passed

Added ParticleSystemFactoryNew (empty Cascade system, zero emitters), ModelContextProtocolToolLibraryFactory and ModelContextProtocolEditorToolLibraryFactory. All three were created and saved under `/Game/UnrealBPDemo/FactoryCommands`; actual classes were read back. Both Blueprint libraries compiled and report BPTYPE_FunctionLibrary with their factory-defined native parents. Custom parent overrides and tool-function authoring are outside this creation configuration.

Physics Asset generation is separately available through `create physics_asset from PATH`, using the existing PhysicsAssetToolset rather than the modal PhysicsAssetFactory. The demo produced 17 bodies, preserved the mesh assignment, and rejected an existing destination. This specialized command is not counted among the 163 generic factory rules.

### Current verification: 165 rules passed

InteractiveToolsPresetCollectionAssetFactory and NiagaraDataChannelAssetFactoryNew created and saved in `/Game/UnrealBPDemo/FactoryCommands`, with actual classes read back. The preset collection label matches the requested asset name. Niagara Data Channel creation requires `fx.Niagara.DataChannels.Enabled`; the rule does not enable it. These are empty creation configurations, not configured presets or a tested channel simulation.

PCGGraphInstanceFactory ParentGraph is visible in the full property schema but SetObjectProperties rejected it on a transient factory. No PCG instance or rule was added; a native factory configuration step is needed for parent-backed creation.

### PCG Graph Instance implementation pending live validation

The PCGGraphInstanceFactory rule requires parentGraph and bridge protocol 4. The native bridge configures the exact reflected ParentGraph field after checking factory identity, field type, and parent type. Native build passed; live creation and parent readback await editor restart. There are 166 configured rules, of which 165 have passed creation validation.

### Current verification: 166 rules passed

UnrealBPBridge protocol 4 is loaded. PCGGraphInstanceFactory created and saved `/Game/UnrealBPDemo/FactoryCommands/PCGI_BridgeDemo`; class is `/Script/PCG.PCGGraphInstance`, and its graph property matches `/Game/UnrealBPDemo/SimpleFactories/Demo_PCGGraphFactory`. A ParticleSystem supplied as parentGraph was rejected before creation and the invalid destination was confirmed absent. This validates instance creation and parent assignment, not PCG graph execution.

### Sound effect class selection pending live validation

SoundSourceEffectFactory requires soundEffectSourcepresetClass; SoundSubmixEffectFactory requires soundEffectSubmixPresetClass. Reflected schema names were verified. Protocol 5 adds the native picker filter rejecting abstract, deprecated and superseded preset classes; the existing reference validator checks the specific source/submix base type. Native build passed. Both creation checks await restart. 168 rules are configured; 166 have passed live creation validation.

### Current verification: 168 rules passed

Protocol 5 loaded. SoundSourceEffectFactory created SourceEffect_BridgeDemo as `/Script/Synthesis.SourceEffectBitCrusherPreset`; SoundSubmixEffectFactory created SubmixEffect_BridgeDemo as `/Script/AudioMixer.SubmixEffectReverbPreset`. Both saved under `/Game/UnrealBPDemo/FactoryCommands` and exact classes were read back. Both abstract Engine preset bases were rejected before asset creation; their requested destinations were confirmed absent. This verifies creation with factory defaults, not audio playback or customized effect settings.

### Current verification: 169 rules passed

ControlRigShapeLibraryFactory created and saved ShapeLibrary_FactoryDemo. Readback confirmed ControlRigShapeLibrary class, default sphere shape proxy, Gizmo and XRay material paths, and Color parameter. The rule declares three required_assets with expected classes; creation validates these before invoking the factory. The catalog exposes these dependencies. No custom shape editing was added.

### Current verification: 170 rules passed

ControlRigAssetFactory created and saved `/Game/UnrealBPDemo/FactoryCommands/CR_FactoryDemo`, read back as `/Script/ControlRig.ControlRigRuntimeAsset`. The rule requires RigVM.BlueprintIndependentAssets and exposes no factory overrides. Normal rig creation only; modular rig configuration, rig execution and legacy Blueprint creation are not covered.

### StateTree creation pending live verification

StateTreeFactory requires stateTreeSchemaClass and bridge protocol 6. The bridge calls the factory's public SetSchemaClass method after reproducing the native picker filter (StateTreeSchema ancestry; no abstract/deprecated/superseded/hidden classes). StateTree is an explicit bridge plugin dependency. Native build passed and reflected option name was verified. Creation, root-state and schema readback await restart. 171 rules configured; 170 live-verified.

### Current verification: 171 rules passed

StateTreeFactory created and saved `/Game/UnrealBPDemo/FactoryCommands/ST_BridgeDemo` with CameraDirectorStateTreeSchema. Actual StateTree class, matching schema class and one root state were read back through existing StateTree inspection tools. Abstract StateTreeSchema and unrelated Actor classes were rejected before asset creation; both requested destinations were absent. No StateTree runtime execution was tested.

### Current verification: 174 rules passed

FontFactory created and saved Font_FactoryDemo with Runtime font cache; no font face was imported or configured. NamingTokensFactory returned an Engine Blueprint with NamingTokens parent; EditorUtilityNamingTokensFactory returned EditorUtilityBlueprint with EditorUtilityNamingTokens parent. Both compiled and saved, with class and registry parent readback. Their catalog asset_class is the factory SupportedClass (parent type), not the returned Blueprint asset class; use explicit target before Blueprint editing. No token functions were authored.

### Current verification: 180 rules passed

WorldFactory, ObjectMixerBlueprintFilterFactory, both Interchange Blueprint pipeline factories, NiagaraEmitterFactoryNew and NiagaraSystemFactoryNew created and saved in FactoryCommands. All actual classes were read back; the three Blueprint parents matched the factory defaults and compilation calls passed. World uses current project partition settings. Niagara emitter uses native default modules/renderers; seven required script assets are validated. Niagara System validates RequiredSystemUpdateScript from live NiagaraEditorSettings through existing reflection before creation. No Niagara simulation or pipeline import was tested.

CurveFactory and three AudioSynesthesia factory rules now use a shared concrete_classes filter backed by native protocol 7. Native build passed; live creation remains pending.

### Current verification: 186 rules passed, two disabled conditional rules

CurveFactory and three AudioSynesthesia factories created, saved and returned the selected concrete classes. All four abstract base class attempts were rejected and left no destination asset. Slate style creation returned a ButtonWidgetStyle inside SlateWidgetStyleAsset. Gameplay Ability Blueprint compiled and saved with GameplayAbility parent.

Procedural Foliage and Sprite Atlas Group settings remain false by user decision. Their required_settings rules reject creation while disabled; no positive creation claim is made. Editor Utility parent validation is being added in native protocol 8.

### Current verification: 188 rules passed, two disabled conditional rules

EditorUtilityBlueprintFactory created, compiled and saved normal and function-library variants. Runtime Actor and EditorUtilityWidget parents were rejected with absent destinations. TemplateSequenceFactoryNew created and saved StaticMeshActor template sequence; its postcondition requires exactly one spawnable with the selected class. CameraAssetFactory creation/save passed, but private director reference verification awaits native protocol 9.

### Current verification: 189 rules passed, two disabled conditional rules

CameraAssetFactory now requires protocol 9 and checks the director class through UCameraAsset::GetCameraDirector before returning success. Existing Camera_ClassDemo and new Camera_PostcheckDemo both matched SingleCameraDirector. Protocol 9 is loaded after an authorized save-checked restart. No camera runtime behavior was tested.
