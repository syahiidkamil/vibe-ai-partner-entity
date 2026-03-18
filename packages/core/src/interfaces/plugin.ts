import type { PluginType } from "@vibe-ai-partner/shared";

/**
 * Declares what a plugin is and what it can do.
 * Read at registration time. IDs must be unique within their plugin group.
 *
 * ID format: lowercase, hyphenated (e.g., "live2d", "kokoro-onnx", "kittentts")
 */
export interface IPluginManifest {
  /** Unique identifier within plugin group. Matches .env config values. */
  id: string;

  /** Human-readable display name (e.g., "Live2D Cubism Renderer") */
  name: string;

  /** Semver version string */
  version: string;

  /** Plugin category — only one plugin active per type at a time */
  type: PluginType;

  /** Feature flags the plugin supports (e.g., ["expressions", "motions", "lipsync"]) */
  capabilities: string[];
}

/**
 * Base interface for all plugins. Every plugin has a manifest,
 * can be initialized with config, and can be disposed.
 *
 * Lifecycle: register → initialize(config) → operate → dispose()
 */
export interface IPlugin {
  /** Static metadata about this plugin */
  readonly manifest: IPluginManifest;

  /**
   * Load resources, connect to services, prepare for operation.
   * Called once before the plugin becomes active.
   */
  initialize(config: Record<string, unknown>): Promise<void>;

  /**
   * Release all resources. Called when the plugin is no longer needed.
   * After dispose(), the plugin instance should not be used.
   */
  dispose(): Promise<void>;
}

/**
 * Manages plugin registration and activation.
 * Enforces one active plugin per type (Strategy pattern).
 *
 * Switching flow: deactivate old → initialize new → activate new
 */
export interface IPluginRegistry {
  /** Add a plugin to the registry. Does not initialize or activate it. */
  register(plugin: IPlugin): void;

  /** Get all registered plugins of a given type. */
  getPluginsByType(type: PluginType): IPlugin[];

  /** Get the currently active plugin for a type. Undefined if none active. */
  getActivePlugin(type: PluginType): IPlugin | undefined;

  /**
   * Switch the active plugin for a type.
   * Deactivates the current plugin (if any), initializes the new one, activates it.
   */
  setActivePlugin(type: PluginType, pluginId: string): Promise<void>;
}
