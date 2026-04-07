
You are building FacilityPro Mobile — a React Native (Expo) app that is 
the mobile companion to an existing Next.js web ERP. The UI must exactly 
match the web app's design system.

## GOAL OF PHASE 0
Set up the complete project foundation so that:
1. All configs are correct from day one (no rebuild surprises)
2. All design tokens from the web app are in place as TypeScript constants
3. Custom fonts are loaded and working
4. A branded splash screen and home screen prove the design system works
5. The app successfully runs on a physical Android device

Do NOT build any navigation, auth, or screens beyond what is listed below.
Zero features. Only foundation.

---

## STEP 1 — Project Setup

The project folder already exists. Initialize it as a new Expo project:
```bash
npx create-expo-app . --template blank-typescript
```

Then install ALL of these packages in one command:
```bash
npx expo install \
  expo-camera \
  expo-location \
  expo-task-manager \
  expo-image-manipulator \
  expo-image-picker \
  expo-local-authentication \
  expo-notifications \
  expo-font \
  expo-splash-screen \
  react-native-maps \
  react-native-screens \
  react-native-safe-area-context \
  react-native-gesture-handler \
  react-native-reanimated

npm install \
  @supabase/supabase-js \
  @react-native-async-storage/async-storage \
  @mmkv/react-native \
  zustand \
  @tanstack/react-query \
  @react-navigation/native \
  @react-navigation/native-stack \
  @react-navigation/bottom-tabs \
  @nozbe/watermelondb \
  @babel/plugin-proposal-decorators \
  @babel/plugin-proposal-class-properties \
  lucide-react-native \
  react-native-svg
```

---

## STEP 2 — app.json

Replace the entire app.json with this exact content:
```json
{
  "expo": {
    "name": "FacilityPro",
    "slug": "facilitypro-mobile",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "automatic",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#F8F6F2"
    },
    "assetBundlePatterns": ["**/*"],
    "ios": {
      "supportsTablet": false,
      "bundleIdentifier": "com.facilitypro.mobile"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#F8F6F2"
      },
      "package": "com.facilitypro.mobile"
    },
    "plugins": [
      "expo-font",
      [
        "expo-splash-screen",
        {
          "backgroundColor": "#F8F6F2",
          "image": "./assets/splash.png",
          "imageWidth": 200
        }
      ],
      [
        "expo-camera",
        {
          "cameraPermission": "FacilityPro needs camera access for job photos and QR scanning."
        }
      ],
      [
        "expo-location",
        {
          "locationAlwaysAndWhenInUsePermission": "FacilityPro needs location for guard tracking and attendance verification.",
          "locationAlwaysPermission": "FacilityPro needs background location for guard patrol monitoring.",
          "locationWhenInUsePermission": "FacilityPro needs location for attendance check-in."
        }
      ],
      [
        "expo-notifications",
        {
          "icon": "./assets/notification-icon.png",
          "color": "#EB5E3B",
          "sounds": []
        }
      ],
      "expo-local-authentication",
      "@nozbe/watermelondb/expo-plugin"
    ],
    "extra": {
      "eas": {
        "projectId": "YOUR_EAS_PROJECT_ID"
      }
    }
  }
}
```

Note: Replace YOUR_EAS_PROJECT_ID with the actual project ID from expo.dev 
after running `eas init`.

---

## STEP 3 — babel.config.js

Replace babel.config.js entirely with:
```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      ['@babel/plugin-proposal-decorators', { legacy: true }],
      ['@babel/plugin-proposal-class-properties', { loose: true }],
      'react-native-reanimated/plugin',
    ],
  };
};
```

IMPORTANT: react-native-reanimated/plugin MUST be last in the plugins array.

---

## STEP 4 — eas.json

Create eas.json in the project root:
```json
{
  "cli": {
    "version": ">= 10.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "apk"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

---

## STEP 5 — tsconfig.json

Replace tsconfig.json with:
```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@constants/*": ["src/constants/*"],
      "@components/*": ["src/components/*"],
      "@screens/*": ["src/screens/*"],
      "@navigation/*": ["src/navigation/*"],
      "@hooks/*": ["src/hooks/*"],
      "@lib/*": ["src/lib/*"],
      "@store/*": ["src/store/*"]
    }
  }
}
```

---

## STEP 6 — Folder Structure

Create this exact folder structure. Create empty index.ts placeholder 
files inside each folder so the folders are tracked by git:
src/
constants/
colors.ts
typography.ts
spacing.ts
shadows.ts
statusColors.ts
index.ts
components/
shared/
.gitkeep
screens/
.gitkeep
navigation/
.gitkeep
hooks/
.gitkeep
lib/
supabase.ts
store/
.gitkeep
assets/
fonts/
.gitkeep

---

## STEP 7 — Design Token Files

Create each file with exactly this content:

### src/constants/colors.ts
```typescript
export const LightColors = {
  background:           '#F8F6F2',
  foreground:           '#1E1710',
  card:                 '#FDFCF9',
  cardForeground:       '#1E1710',
  popover:              '#FDFCF9',
  popoverForeground:    '#1E1710',
  primary:              '#EB5E3B',
  primaryForeground:    '#FFFFFF',
  secondary:            '#F4F0EA',
  secondaryForeground:  '#1E1710',
  muted:                '#F0ECE5',
  mutedForeground:      '#7A7266',
  accent:               '#EB5E3B',
  accentForeground:     '#FFFFFF',
  accentSecondary:      '#5B57C7',
  accentSecondaryFg:    '#FFFFFF',
  accentTertiary:       '#4DA894',
  accentTertiaryFg:     '#FFFFFF',
  destructive:          '#EF4444',
  destructiveForeground:'#FFFFFF',
  border:               '#E5DFD5',
  input:                '#E5DFD5',
  ring:                 '#EB5E3B',
  success:              '#15803D',
  successForeground:    '#FFFFFF',
  critical:             '#EF4444',
  criticalForeground:   '#FFFFFF',
  warning:              '#F59E0B',
  warningForeground:    '#000000',
  info:                 '#2563EB',
  infoForeground:       '#FFFFFF',
  sidebarBackground:    '#F2EDE5',
  sidebarForeground:    '#1E1710',
  sidebarPrimary:       '#EB5E3B',
  sidebarPrimaryFg:     '#FFFFFF',
  sidebarAccent:        '#EB5E3B',
  sidebarAccentFg:      '#FFFFFF',
  sidebarBorder:        '#E5DFD5',
  sidebarMuted:         '#7A7266',
};

export const DarkColors = {
  background:           '#141110',
  foreground:           '#F5F3F0',
  card:                 '#1C1917',
  cardForeground:       '#F5F3F0',
  popover:              '#1C1917',
  popoverForeground:    '#F5F3F0',
  primary:              '#EB5E3B',
  primaryForeground:    '#FFFFFF',
  secondary:            '#252220',
  secondaryForeground:  '#F5F3F0',
  muted:                '#252220',
  mutedForeground:      '#8C8278',
  accent:               '#EB5E3B',
  accentForeground:     '#FFFFFF',
  accentSecondary:      '#7E7ADE',
  accentSecondaryFg:    '#FFFFFF',
  accentTertiary:       '#5FC4AD',
  accentTertiaryFg:     '#FFFFFF',
  destructive:          '#C53030',
  destructiveForeground:'#F5F3F0',
  border:               '#2E2A28',
  input:                '#2E2A28',
  ring:                 '#EB5E3B',
  success:              '#22C55E',
  successForeground:    '#FFFFFF',
  critical:             '#EF4444',
  criticalForeground:   '#FFFFFF',
  warning:              '#F59E0B',
  warningForeground:    '#FFFFFF',
  info:                 '#2563EB',
  infoForeground:       '#FFFFFF',
  sidebarBackground:    '#110F0D',
  sidebarForeground:    '#F5F3F0',
  sidebarPrimary:       '#EB5E3B',
  sidebarPrimaryFg:     '#FFFFFF',
  sidebarAccent:        '#1F1C1A',
  sidebarAccentFg:      '#F5F3F0',
  sidebarBorder:        '#252220',
  sidebarMuted:         '#8C8278',
};
```

### src/constants/statusColors.ts
```typescript
export const StatusColors = {
  assetFunctional:     '#22C55E',
  assetMaintenance:    '#F59E0B',
  assetFaulty:         '#EF4444',
  assetDecommissioned: '#6B7280',
  priorityLow:         '#6B7280',
  priorityNormal:      '#3B82F6',
  priorityHigh:        '#F59E0B',
  priorityUrgent:      '#EF4444',
  statusOpen:          '#3B82F6',
  statusAssigned:      '#8B5CF6',
  statusInProgress:    '#F59E0B',
  statusOnHold:        '#6B7280',
  statusCompleted:     '#22C55E',
  statusCancelled:     '#EF4444',
  jobStarted:          '#3B82F6',
  jobPaused:           '#F59E0B',
  jobCompleted:        '#22C55E',
  jobCancelled:        '#EF4444',
  tierPlatinum:        '#A855F7',
  tierGold:            '#F59E0B',
  tierSilver:          '#94A3B8',
  online:              '#22C55E',
  offline:             '#9CA3AF',
  busy:                '#EF4444',
  away:                '#F59E0B',
};
```

### src/constants/typography.ts
```typescript
export const FontFamily = {
  sans:         'PlusJakartaSans_400Regular',
  sansMedium:   'PlusJakartaSans_500Medium',
  sansSemiBold: 'PlusJakartaSans_600SemiBold',
  sansBold:     'PlusJakartaSans_700Bold',
  sansExtraBold:'PlusJakartaSans_800ExtraBold',
  heading:      'DMSans_400Regular',
  headingMedium:'DMSans_500Medium',
  headingSemiBold:'DMSans_600SemiBold',
  headingBold:  'DMSans_700Bold',
  mono:         'JetBrainsMono_400Regular',
  monoMedium:   'JetBrainsMono_500Medium',
};

export const FontSize = {
  xs:    10,
  sm:    12,
  base:  14,
  md:    16,
  lg:    18,
  xl:    20,
  '2xl': 24,
  '3xl': 30,
};

export const FontWeight = {
  light:     '300' as const,
  regular:   '400' as const,
  medium:    '500' as const,
  semibold:  '600' as const,
  bold:      '700' as const,
  extrabold: '800' as const,
};

export const LineHeight = {
  none:    1,
  tight:   1.25,
  snug:    1.375,
  normal:  1.5,
  relaxed: 1.625,
};
```

### src/constants/spacing.ts
```typescript
export const Spacing = {
  xxs:  2,
  xs:   4,
  sm:   8,
  md:   12,
  base: 16,
  lg:   20,
  xl:   24,
  '2xl':32,
};

export const BorderRadius = {
  none:  0,
  sm:    8,
  md:    10,
  lg:    12,
  xl:    16,
  '2xl': 20,
  full:  9999,
};

export const ComponentHeight = {
  buttonSm:  36,
  button:    40,
  buttonLg:  44,
  buttonXl:  48,
  inputSm:   32,
  input:     40,
  inputLg:   48,
  topNav:    64,
  avatarXs:  24,
  avatarSm:  32,
  avatar:    40,
  avatarLg:  48,
  avatarXl:  64,
};
```

### src/constants/shadows.ts
```typescript
export const Shadows = {
  sm: {
    shadowColor: '#1A150D',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#1A150D',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 3,
  },
  lg: {
    shadowColor: '#1A150D',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.08,
    shadowRadius: 25,
    elevation: 6,
  },
  xl: {
    shadowColor: '#1A150D',
    shadowOffset: { width: 0, height: 25 },
    shadowOpacity: 0.15,
    shadowRadius: 50,
    elevation: 10,
  },
};
```

### src/constants/index.ts
```typescript
export * from './colors';
export * from './typography';
export * from './spacing';
export * from './shadows';
export * from './statusColors';
```

---

## STEP 8 — Supabase Client

Create src/lib/supabase.ts:
```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL ?? '';
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? '';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});
```

Create .env in the project root:
EXPO_PUBLIC_SUPABASE_URL=https://wwhbdgwfodumognpkgrf.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=YOUR_ANON_KEY_HERE

Replace YOUR_ANON_KEY_HERE with the actual anon key from Supabase 
Dashboard → Settings → API.

Also create .env.example with the same keys but empty values, and add 
.env to .gitignore.

---

## STEP 9 — Font Loading & App Entry Point

Install Google Font packages:
```bash
npx expo install \
  @expo-google-fonts/plus-jakarta-sans \
  @expo-google-fonts/dm-sans \
  @expo-google-fonts/jetbrains-mono
```

Replace App.tsx entirely with:
```typescript
import {
  PlusJakartaSans_400Regular,
  PlusJakartaSans_500Medium,
  PlusJakartaSans_600SemiBold,
  PlusJakartaSans_700Bold,
  PlusJakartaSans_800ExtraBold,
} from '@expo-google-fonts/plus-jakarta-sans';
import {
  DMSans_400Regular,
  DMSans_500Medium,
  DMSans_600SemiBold,
  DMSans_700Bold,
} from '@expo-google-fonts/dm-sans';
import {
  JetBrainsMono_400Regular,
  JetBrainsMono_500Medium,
} from '@expo-google-fonts/jetbrains-mono';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { useColorScheme } from 'react-native';
import HomeScreen from './src/screens/HomeScreen';

SplashScreen.preventAutoHideAsync();

export default function App() {
  const colorScheme = useColorScheme();

  const [fontsLoaded, fontError] = useFonts({
    PlusJakartaSans_400Regular,
    PlusJakartaSans_500Medium,
    PlusJakartaSans_600SemiBold,
    PlusJakartaSans_700Bold,
    PlusJakartaSans_800ExtraBold,
    DMSans_400Regular,
    DMSans_500Medium,
    DMSans_600SemiBold,
    DMSans_700Bold,
    JetBrainsMono_400Regular,
    JetBrainsMono_500Medium,
  });

  useEffect(() => {
    if (fontsLoaded || fontError) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded, fontError]);

  if (!fontsLoaded && !fontError) {
    return null;
  }

  return <HomeScreen colorScheme={colorScheme ?? 'light'} />;
}
```

---

## STEP 10 — Home Screen (Design System Proof)

Create src/screens/HomeScreen.tsx:

This screen's only job is to show that fonts, colors, and the design 
system all work correctly on device. Build it to look like a polished 
design system showcase page. It should include:

1. A top section showing the FacilityPro logo treatment exactly as 
   specified below — do NOT use an image file, build it in code:
   - A 40×40 rounded box (borderRadius 12) with background #EB5E3B 
     containing white bold "F" text (fontSize 20, fontWeight 700)
   - Next to it: "FacilityPro" in DMSans_700Bold fontSize 18, 
     color #1E1710 (light) / #F5F3F0 (dark)
   - Below that: "ENTERPRISE" in PlusJakartaSans_800ExtraBold fontSize 10, 
     uppercase, letterSpacing 2, color #EB5E3B
   - The logo box has a glow shadow: shadowColor #EB5E3B, shadowOpacity 0.35, 
     shadowRadius 12, elevation 6

2. A color palette row showing 6 swatches:
   Primary (#EB5E3B), Success (#15803D), Warning (#F59E0B), 
   Destructive (#EF4444), Info (#2563EB), Accent Secondary (#5B57C7)
   Each swatch is a 48×48 circle with the color name below it in 
   PlusJakartaSans_500Medium fontSize 10

3. A typography specimen section showing:
   - "Heading" in DMSans_700Bold fontSize 24, color foreground
   - "Body text" in PlusJakartaSans_400Regular fontSize 14, color foreground
   - "LABEL" in PlusJakartaSans_600SemiBold fontSize 10, uppercase, 
     letterSpacing 1.5, color mutedForeground
   - "0x1A2B3C" in JetBrainsMono_400Regular fontSize 13, color foreground

4. Two sample buttons side by side:
   - Primary button: background #EB5E3B, white text "Get Started", 
     borderRadius 12, height 40, PlusJakartaSans_600SemiBold fontSize 14
   - Outline button: transparent background, border #E5DFD5, 
     text "Learn More", same sizing

5. A sample card at the bottom:
   - borderRadius 16, border #E5DFD5, background #FDFCF9 (light) / 
     #1C1917 (dark), padding 20, elevation 1
   - Card title in DMSans_600SemiBold fontSize 16
   - Card description in PlusJakartaSans_400Regular fontSize 13, 
     color #7A7266
   - A green success badge: background rgba(34,197,94,0.15), 
     text color #15803D, text "Active", borderRadius 9999, 
     paddingHorizontal 10, paddingVertical 2, fontSize 12, 
     PlusJakartaSans_600SemiBold

The screen background must be:
- Light mode: #F8F6F2
- Dark mode: #141110
Detect using the colorScheme prop passed in.

The screen must use SafeAreaView and ScrollView.
Use StyleSheet.create for all styles.
Do NOT use any third-party component libraries.
Do NOT use NativeWind or Tailwind.
Only StyleSheet.create + the design tokens from src/constants/.

The HomeScreen component signature is:
```typescript
interface HomeScreenProps {
  colorScheme: 'light' | 'dark';
}
export default function HomeScreen({ colorScheme }: HomeScreenProps)
```

---

## STEP 11 — Asset Placeholders

Create simple placeholder PNG files for:
- assets/icon.png (1024×1024, solid #EB5E3B square)
- assets/splash.png (any size, solid #F8F6F2 background)  
- assets/adaptive-icon.png (1024×1024, solid #EB5E3B)
- assets/notification-icon.png (96×96, solid #EB5E3B)

Use any method to create these — even a solid color PNG is fine for now.

---

## STEP 12 — Verify Zero TypeScript Errors

After creating all files run:
```bash
npx tsc --noEmit
```

Fix every single error before considering Phase 0 complete. 
Zero errors is the only definition of done.

---

## STEP 13 — EAS Build Commands

After zero TypeScript errors, run these in order:
```bash
# 1. Log in to EAS
eas login

# 2. Link project (creates the project ID)
eas init

# 3. Clear Metro cache
npx expo start --clear
# Press Ctrl+C immediately after Metro starts

# 4. Build the development APK
eas build --platform android --profile development
```

Wait for the build to complete (~15 minutes).
Download the APK from the EAS dashboard link.
Uninstall any previous FacilityPro APK from the test device.
Install the new APK.
Run: npx expo start --dev-client
Connect the device and confirm HomeScreen renders correctly.

---

## DEFINITION OF DONE FOR PHASE 0

Phase 0 is complete ONLY when ALL of these are true:
1. npx tsc --noEmit shows zero errors
2. EAS build succeeds without errors
3. APK installs on physical Android device
4. HomeScreen opens and shows:
   - FacilityPro logo with orange glow
   - Color swatches in correct colors
   - All three fonts rendering (Jakarta Sans, DM Sans, JetBrains Mono)
   - Both buttons visible
   - Card with green badge visible
5. Dark mode shows dark background (#141110) when phone is in dark mode
6. No red error screens

Do not proceed to Phase 1 until all 6 conditions are confirmed on device.
