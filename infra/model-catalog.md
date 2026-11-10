# Enable the model catalog in OpenShift AI 3.5

This guide targets **Red Hat OpenShift AI Self-Managed 3.5.x** on an existing
cluster. The catalog needs the `modelregistry` component and the dashboard
catalog menu enabled. Fresh 3.5 installations enable these by default;
upgraded or explicitly customized installations can need changes.

## Requirements

- An installed OpenShift AI 3.5.x Operator, an existing DataScienceCluster (DSC),
  and sufficient platform resources.
- Cluster administrator access for the DSC change; OpenShift AI administrator
  access for dashboard configuration and catalog source management.
- A managed, working OpenShift AI dashboard and user access to it.
- Bash, `oc`, `jq`, and an authenticated `oc` session for the script.

Set the DSC component configuration to:

```yaml
spec:
  components:
    modelregistry:
      managementState: Managed
      registriesNamespace: rhoai-model-registries
```

Preserve an existing `registriesNamespace` value. The operator provisions the
component resources; you do not need to create the namespace yourself.
See Red Hat's [3.5 model registry component procedure](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/managing_model_registries/enabling-the-model-registry-component_managing-model-registries).

In the existing `OdhDashboardConfig` in the application namespace (normally
`redhat-ods-applications`), ensure:

```yaml
spec:
  dashboardConfig:
    disableModelCatalog: false
```

An omitted `disableModelCatalog` uses the 3.5 default, `false`. Setting it to
`true` hides the catalog. `disableModelRegistry` controls the separate registry
menus; the script only changes the catalog flag. See the [3.5 dashboard configuration reference](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/managing_resources/customizing-the-dashboard).

## Run the script

From the repository root, after logging in to the intended cluster:

```bash
bash infra/enable-model-catalog.sh --help
bash infra/enable-model-catalog.sh --dry-run
bash infra/enable-model-catalog.sh
bash infra/enable-model-catalog.sh --check
```

The script verifies an installed 3.5.x Operator, discovers the singleton DSC
and dashboard configuration, and server-validates both merge patches. Normal
execution applies the patches, waits for the model registry operator deployment
and catalog source ConfigMap, and prints the remaining dashboard checks. It
preserves unrelated component settings and catalog sources. The two writes are
not atomic: after a partial failure, fix the reported issue and rerun.

Optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_NAMESPACE` | `redhat-ods-applications` | Existing dashboard and component application namespace |
| `REGISTRIES_NAMESPACE` | `rhoai-model-registries` | Fallback only when the DSC has no namespace configured |
| `TIMEOUT` | `600` | Seconds per readiness phase |

This is a separate, optional step after [the workshop bootstrap](README.md).
The bootstrap does not explicitly enable `modelregistry`. This script does not
install OpenShift AI, provision a model registry database, or deploy models.

## Verify the catalog and its sources

Run `bash infra/enable-model-catalog.sh --check` for a read-only health snapshot.
It checks the installed operator version, component management state and
reconciliation, dashboard flag, active namespace, dashboard/registry UI/operator
and catalog deployment readiness, bundled catalog dependencies when present,
source ConfigMap contents, and catalog Service ports, selector and ready
EndpointSlices. Existing custom namespace settings are honored.

Each check reports `PASS` or `FAIL`. Exit status is `0` when all checks pass and
`1` when a check or prerequisite fails. Prerequisite failures stop the check;
after discovery, health failures are collected so you can see multiple issues.
The option makes no changes and does not wait for reconciliation. It cannot be
combined with `--dry-run`. `TIMEOUT` applies to normal enablement only.

Kubernetes readiness does not confirm source enablement, source connectivity,
visibility filters, catalog API responses, or browser authentication. Complete
these dashboard checks as well:

1. Reload the dashboard and open **AI hub → Models → Catalog** (some 3.5
   screens call this **AI hub → Catalog**). Confirm model cards and details load.
2. As an OpenShift AI administrator, open **Settings → Model resources and
   operations → Model catalog settings**. Enable the intended sources and
   check include/exclude filters. For enabled custom sources, check that
   validation reaches **Connected**.
3. Hugging Face repository sources require external Hugging Face connectivity
   and support public, non-gated models. Gated/private models requiring tokens
   are outside that source feature. See [3.5 catalog source management](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/manage_and_govern_model_catalog_sources/manage-model-catalog-sources-in-dashboard_manage-govern-model-catalog-sources).

Custom YAML sources can also be configured in the `model-catalog-sources`
ConfigMap in the registries namespace. Keep existing entries when editing it.
See the [3.5 OpenShift catalog source procedure](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/manage_and_govern_model_catalog_sources/configuring-model-catalog-sources-in-openshift_manage-govern-model-catalog-sources).

Browsing the catalog does not require you to provision a registry instance or
GPU model server. Registering a model additionally requires access to an
available model registry. Deployment additionally requires the serving platform,
runtime, hardware capacity, and model/image credentials for the selected model;
ModelCar pulls use the global cluster pull secret. See [registering models](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/working_with_the_model_catalog/registering-a-model-from-the-model-catalog_working-model-catalog)
and [deploying catalog models](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/working_with_the_model_catalog/deploying-a-model-from-the-model-catalog_working-model-catalog).

## Troubleshooting

Use the namespace names discovered by the script if your installation uses
custom values:

```bash
oc get datascienceclusters -o yaml
oc get modelregistry.components.platform.opendatahub.io -o yaml
oc get deployment model-registry-operator-controller-manager -n redhat-ods-applications
oc get pods,services,configmaps -n rhoai-model-registries
oc get odhdashboardconfigs -n redhat-ods-applications -o yaml
oc get events -n rhoai-model-registries --sort-by=.lastTimestamp
```

If the menu is missing, inspect the dashboard flag and reload. If the catalog is
empty, inspect source enablement, visibility filters, backend pod readiness and
source connectivity. A running registry operator alone does not establish that
the catalog API can return model cards. For component reconciliation failures,
inspect DSC and modelregistry conditions before changing other components.
