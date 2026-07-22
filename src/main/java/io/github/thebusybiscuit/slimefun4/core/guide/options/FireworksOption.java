package io.github.thebusybiscuit.slimefun4.core.guide.options;

import io.github.bakedlibs.dough.data.persistent.PersistentDataAPI;
import io.github.bakedlibs.dough.items.CustomItemStack;
import io.github.thebusybiscuit.slimefun4.api.SlimefunAddon;
import io.github.thebusybiscuit.slimefun4.core.config.SlimefunConfigManager;
import io.github.thebusybiscuit.slimefun4.implementation.Slimefun;
import java.util.Optional;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;

class FireworksOption implements SlimefunGuideOption<Boolean> {

    @Override
    public SlimefunAddon getAddon() {
        return Slimefun.instance();
    }

    @Override
    public NamespacedKey getKey() {
        return new NamespacedKey(Slimefun.instance(), "research_fireworks");
    }

    @Override
    public Optional<ItemStack> getDisplayItem(Player p, ItemStack guide) {
        SlimefunConfigManager cfgManager = Slimefun.getConfigManager();

        if (cfgManager.isResearchingEnabled() && cfgManager.isResearchFireworkEnabled()) {
            boolean enabled = getSelectedOption(p, guide).orElse(true);
            ItemStack item = new CustomItemStack(
                    Material.FIREWORK_ROCKET,
                    "&bFirework Effects: &" + (enabled ? "aEnabled" : "4Disabled"),
                    "",
                    "&7Choose whether to display",
                    "&7firework effects whenever",
                    "&7you unlock a new item.",
                    "",
                    "&7\u21E8 &eClick to " + (enabled ? "disable" : "enable") + " firework effects");
            return Optional.of(item);
        } else {
            return Optional.empty();
        }
    }

    @Override
    public void onClick(Player p, ItemStack guide) {
        setSelectedOption(p, guide, !getSelectedOption(p, guide).orElse(true));
        SlimefunGuideSettings.openSettings(p, guide);
    }

    @Override
    public Optional<Boolean> getSelectedOption(Player p, ItemStack guide) {
        NamespacedKey key = getKey();
        boolean value = !PersistentDataAPI.hasByte(p, key) || PersistentDataAPI.getByte(p, key) == (byte) 1;
        return Optional.of(value);
    }

    @Override
    public void setSelectedOption(Player p, ItemStack guide, Boolean value) {
        PersistentDataAPI.setByte(p, getKey(), value.booleanValue() ? (byte) 1 : (byte) 0);
    }
}
