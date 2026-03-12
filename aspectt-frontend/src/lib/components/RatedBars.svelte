<script lang="ts">
	import type { RatedElement } from '$lib/api/client';
	import Tooltip from './Tooltip.svelte';

	let { items, maxValue = 5, showLevel = true, descriptions = {} }: {
		items: RatedElement[];
		maxValue?: number;
		showLevel?: boolean;
		descriptions?: Record<string, string>;
	} = $props();
</script>

<div class="rated-list">
	{#each items as item}
		<div class="bar-row">
			{#if descriptions[item.element_id]}
				<span class="bar-label">
					<Tooltip text={descriptions[item.element_id]}>
						{item.element_name}
					</Tooltip>
				</span>
			{:else}
				<span class="bar-label">{item.element_name}</span>
			{/if}
			<div class="bar-track">
				{#if item.value_IM !== undefined}
					<div
						class="bar-fill importance"
						style="width: {(item.value_IM / maxValue) * 100}%"
						title="Importance: {item.value_IM.toFixed(2)}"
					></div>
				{/if}
			</div>
			<span class="bar-value">{item.value_IM?.toFixed(1) ?? '—'}</span>
			{#if showLevel}
				<div class="bar-track">
					{#if item.value_LV !== undefined}
						<div
							class="bar-fill level"
							style="width: {(item.value_LV / (maxValue + 2)) * 100}%"
							title="Level: {item.value_LV.toFixed(2)}"
						></div>
					{/if}
				</div>
				<span class="bar-value">{item.value_LV?.toFixed(1) ?? '—'}</span>
			{/if}
		</div>
	{/each}
</div>

{#if items.length > 0 && showLevel}
	<div class="legend">
		<span class="legend-item"><span class="swatch importance"></span> Importance</span>
		<span class="legend-item"><span class="swatch level"></span> Level</span>
	</div>
{/if}

<style>
	.rated-list {
		margin-top: 0.5rem;
	}

	.legend {
		display: flex;
		gap: 1.5rem;
		justify-content: flex-end;
		margin-top: 0.5rem;
		font-size: 0.8rem;
		color: var(--color-text-secondary);
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 0.3rem;
	}

	.swatch {
		display: inline-block;
		width: 12px;
		height: 12px;
		border-radius: 2px;
	}

	.swatch.importance {
		background: var(--color-accent);
	}

	.swatch.level {
		background: var(--color-success);
	}
</style>
