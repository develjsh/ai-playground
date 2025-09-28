const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');

/**
 * Metro configuration
 * https://reactnative.dev/docs/metro
 *
 * @type {import('@react-native/metro-config').MetroConfig}
 */
const config = {
  resolver: {
    // 파일 확장자 확인 순서를 명시적으로 설정합니다.
    // .tsx와 .ts를 .js보다 우선적으로 찾게 됩니다.
    sourceExts: ['tsx', 'ts', 'js', 'jsx', 'json'],
  },
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);