<template>
  <div class="container">
    <div class="m-2"></div>
    <h1>
      Db2 地理空間デモ
    </h1>
    <div class="m-2"></div>
    <div class="row">
      <div class="col">
        <a href="https://ibm.box.com/v/WoCSpatial-20220530" target="_blank" rel="noopener noreferrer">
        説明資料
        </a>
      </div>
    </div>
    <div class="m-2"></div>
    <div class="row">
      <div class="col">

        指定された場所から、指定されたメートル以内のシェアサイクルポートをDb2のテーブルをSELECTして最大100件見つけます !
        <p></p>
        <ul>
          <li>場所の指定方法: ポートを見つけたい場所をクリックするか、緯度と経度を入力</li>
          <li>距離の指定方法: 下のフォームの距離に数字を入力</li>
        </ul>
        入力後、「Search」ボタンをクリックしてください。
      </div>
      <div class="m-2"></div>
    </div>
    <div class="row">
      <div class="col">
        <div class="form-group">
          <label class="col-form-label" for="inputDefault">緯度</label>
          <input type="text" v-bind:disabled="isLoading" v-model="inputLat" class="form-control" placeholder="緯度"
            id="inputLat">
        </div>
      </div>
      <div class="col">
        <div class="form-group">
          <label class="col-form-label" for="inputDefault">経度</label>
          <input type="text" v-bind:disabled="isLoading" v-model="inputLon" class="form-control" placeholder="経度"
            id="inputLon">
        </div>
      </div>
      <div class="col col-1 align-self-end">
        <div class="form-group">
          <p>から</p>
        </div>
      </div>
      <div class="col">
        <div class="form-group">
          <label class="col-form-label" for="inputDefault">距離(メートル)</label>
          <input type="text" v-bind:disabled="isLoading" v-model="inputDist" class="form-control" placeholder="100"
            id="inputDist">
        </div>
      </div>
      <div class="col align-self-end">
        <div class="form-group">
          <p>メートル以内の<br/>シェアサイクルポート</p>
        </div>
      </div>
      <div class="col col-1 align-self-end">
        <button type="button" v-bind:disabled="isLoading" class="btn btn-primary" @click="search">Search</button>
      </div>
    </div>

    <div class="m-2"></div>
    <div class="row">
      <div class="col" v-show="isLoading">
        <div class="progress">
          <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="100"
            aria-valuemin="0" aria-valuemax="100" style="width: 100%; ">Loading......</div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <p :class="textClass">{{ searchMessage }}</p>
      </div>
    </div>

    <div class="row">
      <div class="col">
        <div class="alert alert-dismissible alert-primary"  v-if="sqlStr.length > 0">
          <button type="button" class="btn-close" data-bs-dismiss="alert" @click="removeSQL"></button>
          <strong>SQL: </strong> <br/>{{ sqlStr }}
        </div>
      </div>
    </div>



    <div class="row mt-3">
      <div class="col">
        <div style="height:400px;">
          <l-map ref="map" :zoom="zoom" :use-global-leaflet="false" :center="center" @click="moveMarker">
            <l-tile-layer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base"
              name="OpenStreetMap"></l-tile-layer>
            <l-marker :lat-lng="markerLatLng" :icon="icon_search"></l-marker>

            <l-marker v-for="(data, index) in portdata" :key="index" :lat-lng="[data[3], data[2]]">
              <l-tooltip>{{ data[0] }}<br>収容数: {{ data[1] }}, 距離: {{ Math.round(data[3]) }} m</l-tooltip>

            </l-marker>

            <l-marker v-if="isHilight" :lat-lng="hilightLatLng" :icon="icon_hilight">
              <l-tooltip>{{ portdata[hilightIndex][0] }}<br>収容数: {{ portdata[hilightIndex][1] }}, 距離: {{
                Math.round(portdata[hilightIndex][3]) }} m</l-tooltip>
            </l-marker>

          </l-map>
        </div>
      </div>
      <!-- </div>

    <div class="row mt-3"> -->
      <div class="col">
        <p v-if="portdata.length">行をクリックすると該当のポートに緑のピンが表示されます。</p>
        <table class="table table-hover">
          <thead>
            <tr v-if="portdata.length > 0">
              <th scope="col" />
              <th scope="col">ポート名</th>
              <th scope="col">収容数</th>
              <th scope="col">距離(m) </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(data, index) in portdata" :key="index" @click="hilightMarker(e, index)">
              <th scope="row">{{ index + 1 }}</th>
              <td>{{ data[0] }}</td>
              <td>{{ data[1] }}</td>
              <td>{{ Math.round(data[4]) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import L from 'leaflet';
import { LMap, LTileLayer, LMarker, LIcon, LTooltip } from "@vue-leaflet/vue-leaflet";
const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT;
console.log(import.meta.env.VITE_API_ENDPOINT);

export default {
  components: {
    LMap,
    LTileLayer,
    LMarker,
    LIcon, LTooltip
  },
  data() {
    return {
      zoom: 15,
      center: [35.6769883, 139.7588499],
      inputLat: 35.6769883,
      inputLon: 139.7588499,
      inputDist: 1000,
      markerLatLng: [35.6769883, 139.7588499],
      hilightLatLng: [],
      hilightIndex: 0,
      isLoading: false,
      isHilight: false,
      searchMessage: "",
      textClass: 'text-primary',
      portdata: [],
      sqlStr: "",
      icon_search: L.icon({
        iconUrl: '/icon/bikeman_pink_pin.png',
        iconSize: [32, 49],
        iconAnchor: [16, 49]
      }),
      icon_hilight: L.icon({
        iconUrl: '/icon/bike_pin.png',
        iconSize: [32, 49],
        iconAnchor: [16, 49]
      }),

    }
  },
  methods: {
    search(e) {
      this.center = [this.inputLat, this.inputLon]
      this.markerLatLng = this.center
      this.isHilight = false;
      this.sqlStr=""

      this.textClass = 'text-secondary'
      this.searchMessage = "Db2に問い合わせ中"

      this.isLoading = true;
      this.portdata = []



      const requestOptions = {
        method: "POST",
        mode: "cors",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'lat': this.inputLat, 'lon': this.inputLon, 'dist': this.inputDist }),
      };
      console.log(requestOptions);

      fetch(API_ENDPOINT + "/getLoc", requestOptions)
        .then((res) => {
          return res.json();
        })
        .then((json) => {
          if (json.status === "ERROR") {
            this.textClass = 'text-danger';
            this.searchMessage = json.message;
            return;
          }
          this.sqlStr = json.sql;
          if (json.count === 0) {
            this.textClass = 'text-warning';
            this.searchMessage = this.inputDist + "メートル以内のポートは見つかりませんでした";
            return;
          }
          this.portdata = json.message.data;
          this.textClass = 'text-success';
          if (json.count > 100)
            this.searchMessage = json.count + '件見つかりました。近い順に100件のみ表示します。';
          else
            this.searchMessage = json.count + '件見つかりました';
        })
        .catch((error) => {
          this.textClass = 'text-danger';
          this.searchMessage = "Error for accesing to " + API_ENDPOINT + "/getLoc";
          return;
        })
        .finally(() => {
          this.isLoading = false;
          return;
        });



    },
    moveMarker(e) {
      if (!e.latlng) { return; }
      this.textClass = 'text-danger'
      this.center = [e.latlng.lat, e.latlng.lng]
      this.markerLatLng = this.center
      this.inputLat = e.latlng.lat
      this.inputLon = e.latlng.lng
    },
    hilightMarker(e, index) {
      console.log(index);
      this.hilightIndex = index;
      this.isHilight = true;
      this.hilightLatLng = [this.portdata[index][3], this.portdata[index][2]];
      this.center = this.hilightLatLng;
    },
    removeSQL(e){
      this.sqlStr=""
    }

  }
}
</script>

<style></style>