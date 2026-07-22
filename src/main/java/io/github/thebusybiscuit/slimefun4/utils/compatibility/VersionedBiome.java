package io.github.thebusybiscuit.slimefun4.utils.compatibility;

import io.github.thebusybiscuit.slimefun4.implementation.Slimefun;
import java.lang.reflect.Method;
import javax.annotation.Nonnull;
import org.bukkit.block.Biome;

/**
 * Biome 多版本兼容
 *
 * @author ybw0014
 */
public final class VersionedBiome {

    private VersionedBiome() {
        // utility class
    }

    private static final Method VALUE_OF_METHOD;

    static {
        Method valueOfMethod = null;

        try {
            valueOfMethod = Biome.class.getMethod("valueOf", String.class);
        } catch (Exception e) {
            Slimefun.logger().severe("Failed to initialise biome compatibility helper: " + e.getMessage());
        }

        VALUE_OF_METHOD = valueOfMethod;
    }

    @Nonnull
    public static Biome valueOf(@Nonnull String biomeName) throws IllegalArgumentException {
        if (biomeName == null || biomeName.isEmpty()) {
            throw new IllegalArgumentException("Biome name cannot be empty");
        }
        try {
            if (VALUE_OF_METHOD != null) {
                return (Biome) VALUE_OF_METHOD.invoke(null, biomeName.toUpperCase());
            }
        } catch (Exception e) {
            throw new IllegalArgumentException("Unable to invoke Biome.valueOf for name: " + biomeName, e);
        }
        throw new IllegalArgumentException("Biome.valueOf method unavailable");
    }
}
