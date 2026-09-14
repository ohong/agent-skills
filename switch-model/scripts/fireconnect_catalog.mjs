// FireConnect 0.9.6's public CLI collapses pinned models to latest aliases.
// Use its catalog builder before that display filter so exact IDs retain metadata.
import { pathToFileURL } from 'node:url';
import path from 'node:path';
const [source, directory, modelId] = process.argv.slice(2);
try {
  const lib = path.join(source, 'packages/setup-cli/lib');
  const { fetchServerlessCatalogRaw } = await import(pathToFileURL(path.join(lib, 'fireworks/models.mjs')));
  const { buildCodexCatalog } = await import(pathToFileURL(path.join(lib, 'harnesses/codex/catalog.mjs')));
  const { enableCodexFireworks } = await import(pathToFileURL(path.join(lib, 'harnesses/codex/core.mjs')));
  const catalog = buildCodexCatalog(await fetchServerlessCatalogRaw(process.env.FIREWORKS_API_KEY));
  await enableCodexFireworks({
    configPath: path.join(directory, '.codex/config.toml'),
    dataDir: path.join(directory, 'state'),
    catalogPath: path.join(directory, '.codex/fireworks-model-catalog.json'),
    apiKey: process.env.FIREWORKS_API_KEY,
    modelId,
    catalog,
  });
} catch (error) {
  // Avoid leaking credentials contained in an upstream diagnostic.
  const message = String(error.message).replaceAll(process.env.FIREWORKS_API_KEY || 'UNSET', '[redacted]');
  process.stderr.write(`FireConnect catalog integration failed: ${message}\n`);
  process.exitCode = 1;
}
