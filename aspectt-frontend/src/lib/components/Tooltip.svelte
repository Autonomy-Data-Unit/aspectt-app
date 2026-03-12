<script lang="ts">
	import type { Snippet } from 'svelte';

	let { text, children }: {
		text: string;
		children: Snippet;
	} = $props();

	let visible = $state(false);
	let x = $state(0);
	let y = $state(0);
	let tooltipEl: HTMLDivElement | undefined = $state();

	function show(e: MouseEvent) {
		x = e.clientX;
		y = e.clientY;
		visible = true;
	}

	function move(e: MouseEvent) {
		x = e.clientX;
		y = e.clientY;
	}

	function hide() {
		visible = false;
	}
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<span class="tooltip-trigger" onmouseenter={show} onmousemove={move} onmouseleave={hide}>
	{@render children()}
</span>

{#if visible}
	<div class="tooltip" bind:this={tooltipEl}
		style="left: {x}px; top: {y}px;">
		{text}
	</div>
{/if}

<style>
	.tooltip-trigger {
		text-decoration: underline dotted var(--color-border-hover);
		text-underline-offset: 2px;
		cursor: help;
	}

	.tooltip {
		position: fixed;
		z-index: 9999;
		max-width: 340px;
		padding: 0.5rem 0.75rem;
		background: var(--color-surface);
		color: var(--color-text);
		font-size: 0.8rem;
		line-height: 1.45;
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		box-shadow: var(--shadow);
		pointer-events: none;
		transform: translate(12px, -100%);
		margin-top: -8px;
	}
</style>
