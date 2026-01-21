import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Switch } from '../ui/switch';
import { SettingsSection } from './SettingsSection';
import { AgentProfileSettings } from './AgentProfileSettings';
import {
  AVAILABLE_MODELS,
  THINKING_LEVELS,
  DEFAULT_FEATURE_MODELS,
  DEFAULT_FEATURE_THINKING,
  FEATURE_LABELS
} from '../../../shared/constants';
import type {
  AppSettings,
  FeatureModelConfig,
  FeatureThinkingConfig,
  ModelTypeShort,
  ThinkingLevel,
  ToolDetectionResult,
  CliToolSelection
} from '../../../shared/types';
import type { CliToolSelection as CliToolSelectionType } from '../../../shared/types/ipc';

interface GeneralSettingsProps {
  settings: AppSettings;
  onSettingsChange: (settings: AppSettings) => void;
  section: 'agent' | 'paths';
}

/**
 * Helper component to display auto-detected CLI tool information
 */
interface ToolDetectionDisplayProps {
  info: ToolDetectionResult | null;
  isLoading: boolean;
  t: (key: string) => string;
}

function ToolDetectionDisplay({ info, isLoading, t }: ToolDetectionDisplayProps) {
  if (isLoading) {
    return (
      <div className="text-xs text-muted-foreground mt-1">
        Detecting...
      </div>
    );
  }

  if (!info || !info.found) {
    return (
      <div className="text-xs text-muted-foreground mt-1">
        {t('general.notDetected')}
      </div>
    );
  }

  const getSourceLabel = (source: ToolDetectionResult['source']): string => {
    const sourceMap: Record<ToolDetectionResult['source'], string> = {
      'user-config': t('general.sourceUserConfig'),
      'venv': t('general.sourceVenv'),
      'homebrew': t('general.sourceHomebrew'),
      'nvm': t('general.sourceNvm'),
      'system-path': t('general.sourceSystemPath'),
      'bundled': t('general.sourceBundled'),
      'fallback': t('general.sourceFallback'),
    };
    return sourceMap[source] || source;
  };

  return (
    <div className="text-xs text-muted-foreground mt-1 space-y-0.5">
      <div>
        <span className="font-medium">{t('general.detectedPath')}:</span>{' '}
        <code className="bg-muted px-1 py-0.5 rounded">{info.path}</code>
      </div>
      {info.version && (
        <div>
          <span className="font-medium">{t('general.detectedVersion')}:</span>{' '}
          {info.version}
        </div>
      )}
      <div>
        <span className="font-medium">{t('general.detectedSource')}:</span>{' '}
        {getSourceLabel(info.source)}
      </div>
    </div>
  );
}

/**
 * General settings component for agent configuration and paths
 */
export function GeneralSettings({ settings, onSettingsChange, section }: GeneralSettingsProps) {
  const { t } = useTranslation('settings');

  // CLI Tool Selection state
  const [cliToolSelection, setCliToolSelection] = useState<CliToolSelectionType | null>(null);
  const [isLoadingCliTool, setIsLoadingCliTool] = useState(false);

  // Fetch CLI tool selection on mount
  useEffect(() => {
    window.electronAPI.getCliToolSelection()
      .then((result: { success: boolean; data?: CliToolSelectionType }) => {
        if (result.success && result.data) {
          setCliToolSelection(result.data);
        }
      })
      .catch((error: unknown) => {
        console.error('Failed to fetch CLI tool selection:', error);
      });
  }, []);

  const handleToolChange = useCallback(async (tool: 'auto' | 'claude' | 'opencode') => {
    setIsLoadingCliTool(true);
    try {
      await window.electronAPI.setCliTool(tool);
      setCliToolSelection({ selectedTool: tool, autoDetect: tool === 'auto' });
      onSettingsChange({ ...settings, cliTool: tool });
    } catch (error) {
      console.error('Failed to set CLI tool:', error);
    } finally {
      setIsLoadingCliTool(false);
    }
  }, [settings, onSettingsChange]);

  const [toolsInfo, setToolsInfo] = useState<{
    python: ToolDetectionResult;
    git: ToolDetectionResult;
    gh: ToolDetectionResult;
    claude: ToolDetectionResult;
  } | null>(null);
  const [isLoadingTools, setIsLoadingTools] = useState(false);

  // Fetch CLI tools detection info when component mounts (paths section only)
  useEffect(() => {
    if (section === 'paths') {
      setIsLoadingTools(true);
      window.electronAPI
        .getCliToolsInfo()
        .then((result: { success: boolean; data?: { python: ToolDetectionResult; git: ToolDetectionResult; gh: ToolDetectionResult; claude: ToolDetectionResult } }) => {
          if (result.success && result.data) {
            setToolsInfo(result.data);
          }
        })
        .catch((error: unknown) => {
          console.error('Failed to fetch CLI tools info:', error);
        })
        .finally(() => {
          setIsLoadingTools(false);
        });
    }
  }, [section]);

  if (section === 'agent') {
    return (
      <div className="space-y-8">
        {/* CLI Tool Selection */}
        <SettingsSection
          title="CLI Tool Selection"
          description="Choose which AI coding tool to use for Auto Claude operations. Default: Claude Code."
        >
          <div className="space-y-4">
            <Label htmlFor="cliTool" className="text-sm font-medium text-foreground">
              Selected CLI Tool
            </Label>
            <p className="text-sm text-muted-foreground mb-3">
              Select which CLI tool Auto Claude should use. The selected tool will be used for all AI interactions.
            </p>
            <Select
              value={settings.cliTool || 'auto'}
              onValueChange={handleToolChange}
              disabled={isLoadingCliTool}
            >
              <SelectTrigger id="cliTool" className="w-full max-w-md">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto-Detect (Recommended)</SelectItem>
                <SelectItem value="claude">Claude Code (Default)</SelectItem>
                <SelectItem value="opencode">Opencode</SelectItem>
              </SelectContent>
            </Select>
            {cliToolSelection && cliToolSelection.autoDetect && (
              <p className="text-xs text-muted-foreground mt-2">
                <span className="font-medium">Current:</span> {settings.cliTool === 'auto' ? 'Auto-Detect' : settings.cliTool === 'claude' ? 'Claude Code' : settings.cliTool}
              </p>
            )}
          </div>
        </SettingsSection>

        {/* Agent Profile Selection */}
        <AgentProfileSettings />

        {/* Other Agent Settings */}
        <SettingsSection
          title={t('general.otherAgentSettings')}
          description={t('general.otherAgentSettingsDescription')}
        >
          <div className="space-y-6">
            <div className="space-y-3">
              <Label htmlFor="agentFramework" className="text-sm font-medium text-foreground">{t('general.agentFramework')}</Label>
              <p className="text-sm text-muted-foreground">{t('general.agentFrameworkDescription')}</p>
              <Select
                value={settings.agentFramework}
                onValueChange={(value) => onSettingsChange({ ...settings, agentFramework: value })}
              >
                <SelectTrigger id="agentFramework" className="w-full max-w-md">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto-claude">{t('general.agentFrameworkAutoClaude')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between max-w-md">
                <div className="space-y-1">
                  <Label htmlFor="autoNameTerminals" className="text-sm font-medium text-foreground">
                    {t('general.aiTerminalNaming')}
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    {t('general.aiTerminalNamingDescription')}
                  </p>
                </div>
                <Switch
                  id="autoNameTerminals"
                  checked={settings.autoNameTerminals}
                  onCheckedChange={(checked) => onSettingsChange({ ...settings, autoNameTerminals: checked })}
                />
              </div>
            </div>

            {/* Feature Model Configuration */}
            <div className="space-y-4 pt-4 border-t border-border">
              <div className="space-y-1">
                <Label className="text-sm font-medium text-foreground">{t('general.featureModelSettings')}</Label>
                <p className="text-sm text-muted-foreground">
                  {t('general.featureModelSettingsDescription')}
                </p>
              </div>

              {(Object.keys(FEATURE_LABELS) as Array<keyof FeatureModelConfig>).map((feature) => {
                const featureModels = settings.featureModels || DEFAULT_FEATURE_MODELS;
                const featureThinking = settings.featureThinking || DEFAULT_FEATURE_THINKING;

                return (
                  <div key={feature} className="space-y-2">
                    <div className="flex items-center justify-between max-w-md">
                      <Label className="text-sm font-medium text-foreground">
                        {FEATURE_LABELS[feature].label}
                      </Label>
                      <span className="text-xs text-muted-foreground">
                        {FEATURE_LABELS[feature].description}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 max-w-md">
                      {/* Model Select */}
                      <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">{t('general.model')}</Label>
                        <Select
                          value={featureModels[feature]}
                          onValueChange={(value) => {
                            const newFeatureModels = { ...featureModels, [feature]: value as ModelTypeShort };
                            onSettingsChange({ ...settings, featureModels: newFeatureModels });
                          }}
                        >
                          <SelectTrigger className="h-9">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {AVAILABLE_MODELS.map((m) => (
                              <SelectItem key={m.value} value={m.value}>
                                {m.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      {/* Thinking Level Select */}
                      <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">{t('general.thinkingLevel')}</Label>
                        <Select
                          value={featureThinking[feature]}
                          onValueChange={(value) => {
                            const newFeatureThinking = { ...featureThinking, [feature]: value as ThinkingLevel };
                            onSettingsChange({ ...settings, featureThinking: newFeatureThinking });
                          }}
                        >
                          <SelectTrigger className="h-9">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {THINKING_LEVELS.map((level) => (
                              <SelectItem key={level.value} value={level.value}>
                                {level.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </SettingsSection>
      </div>
    );
  }

  if (section === 'paths') {
    return (
      <div className="space-y-8">
        <SettingsSection
          title={t('general.pathsTitle')}
          description={t('general.pathsDescription')}
        >
          <div className="space-y-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium text-foreground">{t('general.python')}</Label>
              <ToolDetectionDisplay info={toolsInfo?.python || null} isLoading={isLoadingTools} t={t} />
            </div>
            <div className="space-y-2">
              <Label className="text-sm font-medium text-foreground">{t('general.git')}</Label>
              <ToolDetectionDisplay info={toolsInfo?.git || null} isLoading={isLoadingTools} t={t} />
            </div>
            <div className="space-y-2">
              <Label className="text-sm font-medium text-foreground">{t('general.gh')}</Label>
              <ToolDetectionDisplay info={toolsInfo?.gh || null} isLoading={isLoadingTools} t={t} />
            </div>
            <div className="space-y-2">
              <Label className="text-sm font-medium text-foreground">{t('general.claude')}</Label>
              <ToolDetectionDisplay info={toolsInfo?.claude || null} isLoading={isLoadingTools} t={t} />
            </div>
          </div>
        </SettingsSection>
      </div>
    );
  }

  return null;
}
